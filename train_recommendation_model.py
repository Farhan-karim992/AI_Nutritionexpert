import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib

# Load dataset
data = pd.read_csv(
    "nutrition_dataset_10k.csv"
)

# Encode goal
goal_encoder = LabelEncoder()

data["goal_encoded"] = goal_encoder.fit_transform(
    data["goal"]
)

# Encode target
recommendation_encoder = LabelEncoder()

data["recommendation_encoded"] = (
    recommendation_encoder.fit_transform(
        data["recommendation"]
    )
)

# Features
X = data[
    [
        "calories",
        "protein",
        "fat",
        "carbs",
        "bmi",
        "goal_encoded"
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
    "recommendation_model.pkl"
)

# Save encoders
joblib.dump(
    goal_encoder,
    "goal_encoder.pkl"
)

joblib.dump(
    recommendation_encoder,
    "recommendation_encoder.pkl"
)

print("Recommendation model trained!")