import pandas as pd

from sklearn.ensemble import RandomForestClassifier

from sklearn.preprocessing import LabelEncoder

import joblib

# Load dataset
data = pd.read_csv(
    "personalized_diet_dataset.csv"
)

# Encode goal
goal_encoder = LabelEncoder()

data["goal_encoded"] = goal_encoder.fit_transform(
    data["goal"]
)

# Encode meal time
meal_encoder = LabelEncoder()

data["meal_encoded"] = meal_encoder.fit_transform(
    data["meal_time"]
)

# Encode recommendation
recommendation_encoder = LabelEncoder()

data["recommendation_encoded"] = (
    recommendation_encoder.fit_transform(
        data["recommendation"]
    )
)

# Features
X = data[
    [
        "bmi",
        "goal_encoded",
        "meal_encoded"
    ]
]

# Target
y = data["recommendation_encoded"]

# Train model
model = RandomForestClassifier()

model.fit(X, y)

# Save model
joblib.dump(
    model,
    "diet_model.pkl"
)

# Save encoders
joblib.dump(
    goal_encoder,
    "diet_goal_encoder.pkl"
)

joblib.dump(
    meal_encoder,
    "meal_encoder.pkl"
)

joblib.dump(
    recommendation_encoder,
    "diet_recommendation_encoder.pkl"
)

print("Diet model trained successfully!")