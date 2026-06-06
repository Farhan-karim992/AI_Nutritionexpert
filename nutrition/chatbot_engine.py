import re
import pandas as pd
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
recommendation_model = joblib.load(
    "recommendation_model.pkl"
)

goal_encoder = joblib.load(
    "goal_encoder.pkl"
)

recommendation_encoder = joblib.load(
    "recommendation_encoder.pkl"
)
# Print columns
print(data.columns)

# IMPORTANT:
# Replace this with your REAL column name
food_column = "food"

def analyze_sentence(user_text, profile):

    user_text = user_text.lower()

    stop_words = [
        "i",
        "ate",
        "and",
        "the",
        "a",
        "an",
        "of",
        "with",
        "had"
    ]

    # Extract quantities + foods
    matches = re.findall(
        r'(\d+)?\s*([a-zA-Z]+)',
        user_text
    )

    foods_found = []

    total_calories = 0
    total_protein = 0
    total_fat = 0
    total_carbs = 0

    # Clean column
    data[food_column] = data[
        food_column
    ].astype(str)

    for qty, food in matches:

        qty = int(qty) if qty else 1

        if food in stop_words:
            continue

        # Search dataset
        result = data[
            data[food_column]
            .str.lower()
            .str.contains(
                rf"\b{food}\b",
                regex=True,
                na=False
            )
        ]

        if not result.empty:

            item = result.iloc[0]

            calories = float(
                item["Caloric Value"]
            ) * qty

            protein = float(
                item["Protein"]
            ) * qty

            fat = float(
                item["Fat"]
            ) * qty

            carbs = float(
                item["Carbohydrates"]
            ) * qty

            total_calories += calories
            total_protein += protein
            total_fat += fat
            total_carbs += carbs

            foods_found.append(
                f"{qty} x {food}"
            )
           # Personalized recommendation
        
        # BMI calculation
    height_m = profile.height / 100

    bmi = profile.weight / (height_m ** 2)

    # Encode goal
    goal_mapping = {

    "gain": "muscle_gain",

    "lose": "weight_loss",

    "loss": "weight_loss",

    "maintain": "maintenance",

    "maintenance": "maintenance"
}

    goal = goal_mapping.get(
     profile.goal,
     profile.goal
)

    goal_encoded = goal_encoder.transform(
     [goal]
)[0]

    # ML prediction
    prediction = recommendation_model.predict(
        [[
            total_calories,
            total_protein,
            total_fat,
            total_carbs,
            bmi,
            goal_encoded
        ]]
    )

    # Decode prediction
    recommendation = (
        recommendation_encoder.inverse_transform(
            prediction
        )[0]
    )

    # Human-friendly responses
    recommendation_messages = {

        "excellent":
        "Excellent meal choice for your goal.",

        "healthy":
        "This is a healthy and balanced meal.",

        "balanced":
        "Balanced nutrition intake detected.",

        "unhealthy":
        "This meal may not support your health goal. Reduce processed and high-fat foods."
    }

    recommendation = recommendation_messages.get(
        recommendation,
        recommendation
    )

    # Final chatbot response
    response = f"""
Foods Detected:
{', '.join(foods_found)}

Total Calories: {round(total_calories)} kcal
Protein: {round(total_protein)} g
Fat: {round(total_fat)} g
Carbs: {round(total_carbs)} g

AI Recommendation:
{recommendation}
"""
    


    return response