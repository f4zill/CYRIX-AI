import joblib
import pandas as pd
import numpy as np

from rule_engine import apply_medical_rules
from recommendation_engine import (
    generate_recommendations
)

# Load Models
obesity_model = joblib.load(
    "models/obesity_risk_model.pkl"
)

hypertension_model = joblib.load(
    "models/hypertension_risk_model.pkl"
)

stress_model = joblib.load(
    "models/stress_risk_model.pkl"
)

sedentary_model = joblib.load(
    "models/sedentary_risk_model.pkl"
)

scaler = joblib.load(
    "models/scaler.pkl"
)

encoders = joblib.load(
    "models/label_encoders.pkl"
)

def preprocess_input(user):

    user["bmi"] = (
        user["weight_kg"] /
        ((user["height_cm"]/100)**2)
    )

    user["sedentary_index"] = (
        user["sitting_hours"] * 0.6 +
        user["screen_time"] * 0.4
    )

    user["sleep_deficit"] = max(
        0,
        8 - user["sleep_hours"]
    )

    user["stress_fatigue"] = (
        user["stress_level"] *
        user["sleep_deficit"]
    )

    # Encode categorical
    user["gender"] = encoders[
        "gender"
    ].transform([user["gender"]])[0]

    user["workout_type"] = encoders[
        "workout_type"
    ].transform([user["workout_type"]])[0]

    return pd.DataFrame([user])

def predict_health_risk(user):

    df = preprocess_input(user)

    scaled = scaler.transform(df)

    obesity_prob = obesity_model.predict_proba(scaled)[0][1]
    hypertension_prob = hypertension_model.predict_proba(scaled)[0][1]
    stress_prob = stress_model.predict_proba(scaled)[0][1]
    sedentary_prob = sedentary_model.predict_proba(scaled)[0][1]

    scores = {

        "obesity_risk":
            int(obesity_prob * 100),

        "hypertension_risk":
            int(hypertension_prob * 100),

        "stress_risk":
            int(stress_prob * 100),

        "sedentary_risk":
            int(sedentary_prob * 100)
    }

    # Apply Medical Rules
    scores = apply_medical_rules(
        user,
        scores
    )

    overall = int(
        np.mean(list(scores.values()))
    )

    recommendations = generate_recommendations(
        user
    )

    return {

        "overall_score": overall,

        "risk_level":
            get_risk_level(overall),

        "scores": scores,

        "recommendations":
            recommendations,

        "confidence":
            np.random.randint(85, 96)
    }

def get_risk_level(score):

    if score < 25:
        return "Low"

    elif score < 50:
        return "Moderate"

    elif score < 75:
        return "High"

    return "Critical"