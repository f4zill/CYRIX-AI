import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# Load CYRIX dataset
df = pd.read_csv("cyrix_dataset.csv")

# Features and target
X = df[[
    "age",
    "systolic_bp",
    "diastolic_bp",
    "heart_rate",
    "steps",
    "sleep"
]]

y = df["target"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Save model
joblib.dump(model, "model.pkl")

print("✅ New CYRIX model trained and saved!")