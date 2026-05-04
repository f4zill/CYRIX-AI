import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import StandardScaler

from sklearn.ensemble import (
    RandomForestClassifier,
    GradientBoostingClassifier
)

from xgboost import XGBClassifier

from sklearn.metrics import (
    classification_report,
    accuracy_score
)

# Load Dataset
df = pd.read_csv("data/lifestyle_dataset.csv")

# Encode Categorical Features
encoders = {}

categorical_cols = [
    "gender",
    "workout_type"
]

for col in categorical_cols:

    le = LabelEncoder()

    df[col] = le.fit_transform(df[col])

    encoders[col] = le

# Encode Targets
target_cols = [
    "obesity_risk",
    "hypertension_risk",
    "stress_risk",
    "sedentary_risk"
]

target_encoders = {}

for col in target_cols:

    le = LabelEncoder()

    df[col] = le.fit_transform(df[col])

    target_encoders[col] = le

# Features
X = df.drop(columns=target_cols)

# Scale Features
scaler = StandardScaler()

X_scaled = scaler.fit_transform(X)

# Save scaler
joblib.dump(
    scaler,
    "models/scaler.pkl"
)

# Save encoders
joblib.dump(
    encoders,
    "models/label_encoders.pkl"
)

# Train Function
def train_model(target_name, model):

    y = df[target_name]

    X_train, X_test, y_train, y_test = train_test_split(
        X_scaled,
        y,
        test_size=0.2,
        random_state=42
    )

    model.fit(X_train, y_train)

    preds = model.predict(X_test)

    print(f"\n==== {target_name} ====")

    print(
        classification_report(
            y_test,
            preds
        )
    )

    accuracy = accuracy_score(
        y_test,
        preds
    )

    print("Accuracy:", accuracy)

    joblib.dump(
        model,
        f"models/{target_name}_model.pkl"
    )

# Train Models

train_model(
    "obesity_risk",
    RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        random_state=42
    )
)

train_model(
    "hypertension_risk",
    XGBClassifier(
        n_estimators=200,
        max_depth=5,
        learning_rate=0.05
    )
)

train_model(
    "stress_risk",
    GradientBoostingClassifier()
)

train_model(
    "sedentary_risk",
    RandomForestClassifier(
        n_estimators=150
    )
)

print("\nAll Models Trained")