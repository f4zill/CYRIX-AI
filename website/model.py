import joblib
import os
import numpy as np
import pandas as pd
# Load model
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
model = joblib.load(os.path.join(BASE_DIR, "model.pkl"))


# -----------------------------
# 🧠 Prediction Function
# -----------------------------
def predict_risk(data):
    """
    Expected input:
    data = {
        "age": int,
        "systolic_bp": int,
        "diastolic_bp": int,
        "heart_rate": int,
        "steps": int,
        "sleep": float
    }
    """

    # Convert to feature array (MUST match training order)
    features = np.array([[ 
        data["age"],
        data["systolic_bp"],
        data["diastolic_bp"],
        data["heart_rate"],
        data["steps"],
        data["sleep"]
    ]])

    # Model prediction
    prediction = model.predict(features)[0]

    # Probability → Risk Score
    prob = model.predict_proba(features)[0][1]
    risk_score = round(prob * 100, 2)

    # Risk Level
    if risk_score < 30:
        risk = "LOW 🟢"
    elif risk_score < 60:
        risk = "MODERATE 🟡"
    else:
        risk = "HIGH 🔴"

    # Interpretation Layer
    issues = detect_issues(data)
    recommendations = generate_recommendations(data)

    return {
        "risk": risk,
        "risk_score": risk_score,
        "issues": issues,
        "recommendations": recommendations
    }


# -----------------------------
# 🔍 Issue Detection
# -----------------------------
def detect_issues(data):
    issues = []

    # Blood Pressure
    if data["systolic_bp"] >= 130 or data["diastolic_bp"] >= 80:
        issues.append("Elevated Blood Pressure")

    # Heart Rate
    if data["heart_rate"] > 100:
        issues.append("High Resting Heart Rate")
    elif data["heart_rate"] < 60:
        issues.append("Low Heart Rate")

    # Activity
    if data["steps"] < 5000:
        issues.append("Low Physical Activity")

    # Sleep
    if data["sleep"] < 6:
        issues.append("Poor Sleep")

    return issues


# -----------------------------
# 💡 Recommendation Engine
# -----------------------------
def generate_recommendations(data):
    recs = []

    # BP
    if data["systolic_bp"] >= 130 or data["diastolic_bp"] >= 80:
        recs.append("Reduce sodium intake and monitor blood pressure regularly")

    # Heart Rate
    if data["heart_rate"] > 100:
        recs.append("Engage in regular cardio and stress reduction techniques")

    if data["heart_rate"] < 60:
        recs.append("Consult a doctor if experiencing dizziness or fatigue")

    # Activity
    if data["steps"] < 5000:
        recs.append("Increase daily activity (aim for 8,000–10,000 steps)")

    # Sleep
    if data["sleep"] < 6:
        recs.append("Improve sleep schedule (7–8 hours recommended)")

    # General fallback
    if not recs:
        recs.append("Maintain your current healthy lifestyle")

    return recs


# -----------------------------
# 🧪 Example Test
# -----------------------------
if __name__ == "__main__":
    user_data = {
        "age": 22,
        "systolic_bp": 135,
        "diastolic_bp": 90,  
        "heart_rate": 95,
        "steps": 3000,
        "sleep": 5.5
    }

    result = predict_risk(user_data)
    print("\n🔍 CYRIX RESULT:")
    print(result)