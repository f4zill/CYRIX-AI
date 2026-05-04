def generate_recommendations(user):

    recommendations = []

    if user["sleep_hours"] < 6:
        recommendations.append(
            "Improve sleep duration to 7-8 hours."
        )

    if user["daily_steps"] < 5000:
        recommendations.append(
            "Aim for at least 7000 daily steps."
        )

    if user["water_intake"] < 2:
        recommendations.append(
            "Increase water intake."
        )

    if user["junk_food_frequency"] > 4:
        recommendations.append(
            "Reduce junk food frequency."
        )

    if user["stress_level"] > 7:
        recommendations.append(
            "Practice stress management techniques."
        )

    return recommendations