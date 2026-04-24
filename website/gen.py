import pandas as pd
import numpy as np

def generate_cyrix_dataset(input_path="heart.csv", output_path="cyrix_dataset.csv"):
    # Load dataset
    df = pd.read_csv(input_path)

    # Keep only relevant columns
    df = df[["age", "trestbps", "thalach", "target"]].copy()

    # Rename columns
    df.rename(columns={
        "trestbps": "systolic_bp",
        "thalach": "heart_rate"
    }, inplace=True)

    # Generate diastolic BP (realistic ratio)
    df["diastolic_bp"] = (df["systolic_bp"] * 0.65 + np.random.randint(-5, 6, size=len(df))).astype(int)

    # Generate steps (activity-based on risk)
    df["steps"] = np.where(
        df["target"] == 1,
        np.random.randint(2000, 6000, size=len(df)),   # less active (higher risk)
        np.random.randint(6000, 12000, size=len(df))  # more active (lower risk)
    )

    # Generate sleep hours (based on risk)
    df["sleep"] = np.where(
        df["target"] == 1,
        np.round(np.random.uniform(4.0, 6.0, size=len(df)), 1),  # poor sleep
        np.round(np.random.uniform(6.0, 9.0, size=len(df)), 1)   # healthy sleep
    )

    # Add slight noise to heart rate (realism)
    df["heart_rate"] = df["heart_rate"] + np.random.randint(-3, 4, size=len(df))

    # Clip realistic ranges
    df["heart_rate"] = df["heart_rate"].clip(50, 180)
    df["systolic_bp"] = df["systolic_bp"].clip(90, 200)
    df["diastolic_bp"] = df["diastolic_bp"].clip(60, 120)

    # Reorder columns
    df = df[[
        "age",
        "systolic_bp",
        "diastolic_bp",
        "heart_rate",
        "steps",
        "sleep",
        "target"
    ]]

    # Save dataset
    df.to_csv(output_path, index=False)

    print("✅ CYRIX dataset generated successfully!")
    print(f"Saved as: {output_path}")
    print("\nSample data:")
    print(df.head())


# Run the generator
generate_cyrix_dataset()