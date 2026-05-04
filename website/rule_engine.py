def apply_medical_rules(user, scores):

    if user["blood_pressure_sys"] > 160:
        scores["hypertension_risk"] += 15

    if user["sleep_hours"] < 4:
        scores["stress_risk"] += 20

    if user["stress_level"] > 8:
        scores["stress_risk"] += 10

    if user["daily_steps"] < 2000:
        scores["sedentary_risk"] += 15

    return scores