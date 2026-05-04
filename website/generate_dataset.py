import pandas as pd
import numpy as np

np.random.seed(42)

n = 15000

data = pd.DataFrame({

    "age": np.random.randint(18, 65, n),

    "gender": np.random.choice(
        ["Male", "Female"],
        n
    ),

    "height_cm": np.random.randint(145, 190, n),

    "weight_kg": np.random.randint(45, 120, n),

    "sleep_hours": np.random.normal(6.5, 1.5, n).clip(3, 10),

    "sleep_quality": np.random.randint(1, 10, n),

    "screen_time": np.random.randint(2, 14, n),

    "sitting_hours": np.random.randint(2, 14, n),

    "stress_level": np.random.randint(1, 10, n),

    "water_intake": np.random.uniform(0.5, 5, n),

    "junk_food_frequency": np.random.randint(0, 7, n),

    "sugar_intake": np.random.randint(0, 10, n),

    "meal_consistency": np.random.randint(1, 10, n),

    "outside_food_frequency": np.random.randint(0, 7, n),

    "protein_intake": np.random.randint(1, 10, n),

    "exercise_frequency": np.random.randint(0, 7, n),

    "daily_steps": np.random.randint(1000, 15000, n),

    "workout_type": np.random.choice(
        ["None", "Cardio", "Strength", "Mixed"],
        n
    ),

    "smoking": np.random.choice([0, 1], n),

    "alcohol": np.random.choice([0, 1], n),

    "blood_pressure_sys": np.random.randint(90, 180, n),

    "blood_pressure_dia": np.random.randint(60, 120, n),

    "heart_rate": np.random.randint(55, 120, n),

    "family_history": np.random.choice([0, 1], n)
})

# BMI Calculation
data["bmi"] = (
    data["weight_kg"] /
    ((data["height_cm"] / 100) ** 2)
)

# Feature Engineering
data["sedentary_index"] = (
    data["sitting_hours"] * 0.6 +
    data["screen_time"] * 0.4
)

data["sleep_deficit"] = np.maximum(
    0,
    8 - data["sleep_hours"]
)

data["stress_fatigue"] = (
    data["stress_level"] *
    data["sleep_deficit"]
)

# Target Generation

# Obesity Risk
data["obesity_risk"] = np.where(
    (
        (data["bmi"] > 30) |
        (data["junk_food_frequency"] > 4) |
        (data["exercise_frequency"] < 2)
    ),
    "High",
    "Low"
)

# Hypertension Risk
data["hypertension_risk"] = np.where(
    (
        (data["blood_pressure_sys"] > 140) |
        (data["stress_level"] > 7)
    ),
    "High",
    "Low"
)

# Stress Burnout Risk
data["stress_risk"] = np.where(
    (
        (data["stress_level"] > 7) &
        (data["sleep_hours"] < 5)
    ),
    "High",
    "Low"
)

# Sedentary Risk
data["sedentary_risk"] = np.where(
    (
        (data["daily_steps"] < 4000) |
        (data["sitting_hours"] > 10)
    ),
    "High",
    "Low"
)

# Save Dataset
data.to_csv(
    "data/lifestyle_dataset.csv",
    index=False
)

print("Dataset Generated")