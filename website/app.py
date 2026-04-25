from flask import Flask, render_template, request, jsonify, redirect, session, make_response
from model import predict_risk
from rules import rule_check
from user_service import create_user, login_user
from db import records_collection, users_collection
from datetime import datetime
import json
import os
import uuid

app = Flask(__name__)
app.secret_key = "supersecretkey"

RECORDS_FILE = os.path.join(os.path.dirname(__file__), "records.json")


# ---------------- JSON FILE HELPERS ----------------

def load_json_records():
    if not os.path.exists(RECORDS_FILE):
        return []
    with open(RECORDS_FILE, "r") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_json_records(records):
    with open(RECORDS_FILE, "w") as f:
        json.dump(records, f, indent=2, default=str)


def append_json_record(entry):
    """Prepend a new prediction entry to records.json (newest first)."""
    records = load_json_records()
    records.insert(0, entry)
    save_json_records(records)


def get_user_json_records(user_id, limit=None):
    """Return records for a specific user, newest first."""
    all_records = load_json_records()
    user_records = [r for r in all_records if r.get("user_id") == user_id]
    if limit:
        user_records = user_records[:limit]
    return user_records


# ---------------- HELPERS ----------------

def final_decision(ml, rule):
    ml_risk = ml["risk"]

    if rule["risk"] == "HIGH":
        return "HIGH (Rule Override)"

    if "HIGH" in ml_risk or rule["risk"] == "MODERATE":
        return "MODERATE/HIGH"

    return "LOW"


def is_logged_in():
    return "user_id" in session


def protect_route():
    if not is_logged_in():
        return redirect("/")
    return None


def get_current_user_name():
    if not is_logged_in():
        return None
    user = users_collection.find_one(
        {"user_id": session["user_id"]},
        {"_id": 0, "name": 1}
    )
    return user["name"] if user else "User"


# ---------------- AUTH ----------------

@app.route("/")
def home():
    if is_logged_in():
        return redirect("/dashboard")
    return render_template("login.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        create_user(
            request.form["name"],
            request.form["email"],
            request.form["password"]
        )
        return redirect("/")
    return render_template("register.html")


@app.route("/login", methods=["POST"])
def login():
    user = login_user(
        request.form["email"],
        request.form["password"]
    )

    if user:
        session["user_id"] = user["user_id"]
        session["user_name"] = user["name"]
        return redirect("/dashboard")

    return "Invalid credentials", 401


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ---------------- DASHBOARD ----------------

@app.route("/dashboard")
def dashboard():
    guard = protect_route()
    if guard:
        return guard

    latest = records_collection.find_one(
        {"user_id": session["user_id"]},
        sort=[("timestamp", -1)]
    )

    stats = {
        "heart_rate": 72,
        "bp": "120/80",
        "sleep": 7.5,
        "health_score": 80
    }

    if latest:
        m = latest["metrics"]
        stats["heart_rate"] = m.get("heart_rate", 72)
        stats["bp"] = f"{m.get('systolic_bp', 120)}/{m.get('diastolic_bp', 80)}"
        stats["health_score"] = (
            85 if latest["final_result"] == "LOW"
            else 65 if "MODERATE" in latest["final_result"]
            else 40
        )

    response = make_response(
        render_template(
            "dashboard.html",
            user_id=session["user_id"],
            user_name=session.get("user_name", get_current_user_name()),
            stats=stats
        )
    )
    response.headers["Cache-Control"] = "no-store"
    return response


# ---------------- OTHER PAGES ----------------

@app.route("/profile")
def profile():
    guard = protect_route()
    if guard:
        return guard
    return render_template("profile.html", user_name=session.get("user_name", get_current_user_name()))


@app.route("/plans")
def plans():
    guard = protect_route()
    if guard:
        return guard
    return render_template("plans.html", user_name=session.get("user_name", get_current_user_name()))


@app.route("/records")
def records():
    guard = protect_route()
    if guard:
        return guard
    return render_template("records.html", user_name=session.get("user_name", get_current_user_name()))


@app.route("/session")
def new_session():
    guard = protect_route()
    if guard:
        return guard
    return render_template("session.html", user_name=session.get("user_name", get_current_user_name()))


@app.route("/rules")
def rules_page():
    guard = protect_route()
    if guard:
        return guard
    return render_template("rules.html", user_name=session.get("user_name", get_current_user_name()))


@app.route("/nutrition")
def nutrition():
    guard = protect_route()
    if guard:
        return guard
    return render_template("nutrition.html", user_name=session.get("user_name", get_current_user_name()))


# ---------------- API: PREDICT ----------------

@app.route("/api/predict", methods=["POST"])
def predict():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    try:
        req = request.json

        # ✅ SAFE + FRONTEND COMPATIBLE DATA
        data = {
            "user_id":      session["user_id"],
            "age":          int(req.get("age", 0)),

            # ✅ STANDARDIZED KEYS (THIS IS THE FIX)
            "systolic_bp":  int(req.get("systolic_bp", req.get("trestbps", 120))),
            "diastolic_bp": int(req.get("diastolic_bp", 80)),
            "heart_rate":   int(req.get("heartRate", req.get("thalach", 72))),

            "chol":         int(req.get("chol", 200)),
            "fbs":          int(req.get("fbs", 0)),
            "steps":        int(req.get("steps", 5000)),
            "sleep":        float(req.get("sleep", 7))
        }

        print("DATA SENT TO RULE ENGINE:", data)

        ml_risk     = predict_risk(data)
        rule_result = rule_check(data)
        final_risk  = final_decision(ml_risk, rule_result)

        now = datetime.utcnow()

        # ── MongoDB record (unchanged schema) ──────────────────────────────
        mongo_record = {
            "user_id":      data["user_id"],
            "metrics":      data,
            "ml_result":    ml_risk,
            "rule_result":  rule_result["risk"],
            "final_result": final_risk,
            "reason":       rule_result["reason"],
            "timestamp":    now
        }
        records_collection.insert_one(mongo_record)

        # ── JSON file record (flat, chart-friendly) ────────────────────────
        json_record = {
            "id":        str(uuid.uuid4())[:8],
            "user_id":   data["user_id"],
            "timestamp": now.isoformat(timespec="seconds"),
            "inputs": {
                "age":          data["age"],
                "sex":          int(req.get("sex", 1)),
                "systolic_bp":  data["systolic_bp"],
                "diastolic_bp": data["diastolic_bp"],
                "heart_rate":   data["heart_rate"],
                "chol":         data["chol"],
                "fbs":          data["fbs"],
                "steps":        data["steps"],
                "sleep":        data["sleep"]
            },
            "result": {
                "mlRisk":    ml_risk,
                "ruleRisk":  rule_result["risk"],
                "finalRisk": final_risk,
                "score":     _risk_to_score(final_risk),
                "reason":    rule_result["reason"]
            }
        }
        append_json_record(json_record)

        return jsonify({
            "mlRisk":    ml_risk,
            "ruleRisk":  rule_result["risk"],
            "finalRisk": final_risk,
            "reason":    rule_result["reason"]
        })

    except Exception as e:
        print("ERROR:", str(e))
        return jsonify({"error": str(e)}), 400


def _risk_to_score(risk_str):
    """Convert final risk label to a numeric score for chart display."""
    r = (risk_str or "").upper()
    if "HIGH" in r:
        return 8
    if "MODERATE" in r:
        return 4
    return 1


# ---------------- API: HISTORY ----------------

@app.route("/api/history")
def history():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    # Serve from JSON file for consistent flat structure
    user_records = get_user_json_records(session["user_id"], limit=10)
    return jsonify(user_records)


# ---------------- API: RECORDS SUMMARY (Records dashboard charts) ------------

@app.route("/api/records/summary")
def records_summary():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    user_records = get_user_json_records(session["user_id"])

    entries = []
    for r in user_records:
        inp = r.get("inputs", {})
        res = r.get("result", {})
        entries.append({
            "id":          r.get("id"),
            "timestamp":   r.get("timestamp"),
            "risk":        res.get("finalRisk", ""),
            "score":       res.get("score", 0),
            "reason":      res.get("reason", ""),
            "steps":       inp.get("steps", 0),
            "sleep":       inp.get("sleep", 0),
            "systolic_bp": inp.get("systolic_bp", 0),
            "chol":        inp.get("chol", 0),
            "heart_rate":  inp.get("heart_rate", 0),
            "age":         inp.get("age", 0),
        })

    return jsonify({"count": len(entries), "entries": entries})


# ---------------- API: DASHBOARD DATA ----------------

@app.route("/api/dashboard-data")
def dashboard_data():
    if not is_logged_in():
        return jsonify({"error": "Unauthorized"}), 401

    records = list(records_collection.find(
        {"user_id": session["user_id"]},
        {"_id": 0}
    ).sort("timestamp", -1).limit(7))

    records.reverse()

    heart  = [r["metrics"].get("heart_rate", 72) for r in records if "metrics" in r]
    sleep  = [6 + (i % 3) for i in range(len(heart))]
    labels = ["Day " + str(i + 1) for i in range(len(heart))]

    return jsonify({
        "labels": labels,
        "heart":  heart,
        "sleep":  sleep
    })


# ---------------- RUN ----------------

if __name__ == "__main__":
    app.run(debug=True)