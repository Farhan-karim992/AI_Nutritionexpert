import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score
import joblib

# Load all datasets

data1 = pd.read_csv("FOOD-DATA-GROUP1.csv")
data2 = pd.read_csv("FOOD-DATA-GROUP2.csv")
data3 = pd.read_csv("FOOD-DATA-GROUP3.csv")
data4 = pd.read_csv("FOOD-DATA-GROUP4.csv")
data5 = pd.read_csv("FOOD-DATA-GROUP5.csv")

# Combine datasets

data = pd.concat(
    [data1, data2, data3, data4, data5],
    ignore_index=True
)

print("Columns:")
print(data.columns)

print("\nTotal rows:")
print(len(data))

# Remove missing values

data = data.dropna()

# Features

X = data[
    [
        "Caloric Value",
        "Protein",
        "Fat",
        "Carbohydrates"
    ]
]

# Target

y = data["Nutrition Density"]

# Train/Test Split

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42
)

# Train Model

model = RandomForestRegressor(
    n_estimators=100,
    random_state=42
)

model.fit(
    X_train,
    y_train
)

# Evaluate

predictions = model.predict(X_test)

score = r2_score(
    y_test,
    predictions
)

print("\nModel Accuracy (R² Score):")
print(round(score, 4))

# Save Model

joblib.dump(
    model,
    "nutrition_density_model.pkl"
)

print(
    "\nModel saved as nutrition_density_model.pkl"
)