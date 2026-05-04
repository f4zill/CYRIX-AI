import traceback
from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from datetime import timedelta

from predict import predict_health_risk

from db import (
    create_user,
    save_assessment,
    save_prediction,
    get_user_history,
    login_user
)

app = Flask(__name__)

# =========================
# CONFIG
# =========================
app.secret_key = "cyrix_secret_key"
app.permanent_session_lifetime = timedelta(days=7)

# =========================
# HOME ROUTE (SAFE REDIRECT ONLY)
# =========================
@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard_page"))
    return redirect(url_for("login_page"))

# =========================
# PAGES
# =========================
@app.route("/login")
@app.route("/login.html")
def login_page():
    if "user_id" in session:
        return redirect(url_for("dashboard_page"))
    return render_template("login.html")


@app.route("/register")
@app.route("/register.html")
def register_page():
    if "user_id" in session:
        return redirect(url_for("dashboard_page"))
    return render_template("register.html")


@app.route("/dashboard")
@app.route("/dashboard.html")
def dashboard_page():
    if "user_id" not in session:
        return redirect(url_for("login_page"))
    return render_template("dashboard.html")

# =========================
# REGISTER
# =========================
@app.route("/api/auth/register", methods=["POST"])
def register_user():
    try:
        data = request.get_json()

        first_name = data.get("firstName", "").strip()
        last_name = data.get("lastName", "").strip()
        full_name = f"{first_name} {last_name}".strip()

        email = data.get("email")
        password = data.get("password")
        role = data.get("role", "user")

        profile = data.get("profile", {})
        age = profile.get("age")
        gender = profile.get("gender")

        user = create_user(
            name=full_name,
            email=email,
            password=password,
            age=age,
            gender=gender,
            role=role
        )

        session.clear()
        session.permanent = True
        session["user_id"] = user["user_id"]
        session["name"] = user["name"]
        session["role"] = user["role"]

        return jsonify({
            "success": True,
            "redirect": "/dashboard"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500


# =========================
# LOGIN
# =========================
@app.route("/api/auth/login", methods=["POST"])
def login():
    try:
        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        user = login_user(email, password)

        if not user:
            return jsonify({
                "success": False,
                "message": "Invalid credentials"
            }), 401

        session.clear()
        session.permanent = True
        session["user_id"] = user["user_id"]
        session["name"] = user["name"]
        session["role"] = user.get("role", "user")

        return jsonify({
            "success": True,
            "redirect": "/dashboard"
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# =========================
# VERIFY SESSION (FIXED)
# =========================
@app.route("/api/auth/verify", methods=["GET"])
def verify():
    if "user_id" not in session:
        return jsonify({"logged_in": False}), 401

    return jsonify({
        "logged_in": True,
        "user": {
            "user_id": session["user_id"],
            "name": session["name"],
            "role": session["role"]
        }
    })


# =========================
# LOGOUT (NO REDIRECT LOOP)
# =========================
@app.route("/api/auth/logout", methods=["GET"])
def logout():
    session.clear()
    return jsonify({"success": True})


# =========================
# PROFILE
# =========================
@app.route("/api/user/profile")
def profile():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({
        "user_id": session["user_id"],
        "name": session["name"],
        "role": session["role"]
    })


# =========================
# PREDICT
# =========================
@app.route("/api/predict", methods=["POST"])
def predict():
    try:
        if "user_id" not in session:
            return jsonify({"error": "Unauthorized"}), 401

        data = request.get_json()
        user_id = session["user_id"]

        save_assessment(user_id, data)
        result = predict_health_risk(data)
        save_prediction(user_id, result)

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "error": str(e),
            "trace": traceback.format_exc()
        }), 500


# =========================
# HISTORY
# =========================
@app.route("/api/history")
def history():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401

    data = get_user_history(session["user_id"])
    return jsonify(data)


# =========================
# HEALTH CHECK
# =========================
@app.route("/api/health")
def health():
    return jsonify({
        "status": "CYRIX Running",
        "database": "Connected",
        "ml_engine": "Active"
    })


# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)