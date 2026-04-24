def rule_check(data):
    flags = []
    risk = "LOW"

    hr = data.get("heart_rate", 72)
    bp = data.get("systolic_bp", 120)
    chol = data.get("chol", 200)
    fbs = data.get("fbs", 0)

    # ---------------- CRITICAL ----------------
    if bp >= 180:
        return {"risk": "HIGH", "reason": "Hypertensive Crisis"}

    if hr > 130:
        return {"risk": "HIGH", "reason": "Severe Tachycardia"}

    # ---------------- HEART RATE ----------------
    if hr > 100:
        flags.append("Tachycardia")
        risk = "MODERATE"
    elif hr < 60:
        flags.append("Bradycardia")
        risk = "MODERATE"

    # ---------------- BLOOD PRESSURE ----------------
    if 130 <= bp < 140:
        flags.append("Stage 1 Hypertension")
        risk = "MODERATE"
    elif bp >= 140:
        flags.append("Stage 2 Hypertension")
        risk = "HIGH"
    elif 120 <= bp < 130:
        flags.append("Elevated BP")

    # ---------------- CHOLESTEROL ----------------
    if chol >= 240:
        flags.append("High Cholesterol")
        risk = "HIGH"
    elif 200 <= chol < 240:
        flags.append("Borderline Cholesterol")
        if risk != "HIGH":
            risk = "MODERATE"

    # ---------------- BLOOD SUGAR ----------------
    if fbs >= 126:
        flags.append("Diabetes Range")
        risk = "HIGH"
    elif 100 <= fbs < 126:
        flags.append("Prediabetes")
        if risk == "LOW":
            risk = "MODERATE"

    # ---------------- ESCALATION ----------------
    if len(flags) >= 3:
        risk = "HIGH"

    return {
        "risk": risk,
        "reason": ", ".join(flags) if flags else "Normal"
    }