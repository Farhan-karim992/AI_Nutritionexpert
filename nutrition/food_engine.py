import pandas as pd

# Load dataset
data = pd.read_csv("FOOD-DATA-GROUP1.csv")


def analyze_food(food_name, goal):

    # Search food
    # Search food using partial matching
    result = data[
    data["food"].astype(str)
    .str.lower()
    .str.contains(
        food_name.lower(),
        na=False
    )
]

    # Food not found
    if result.empty:

        return {
            "error": "Food not found"
        }

    # Get first matching food
    food = result.iloc[0]

    calories = food["Caloric Value"]
    protein = food["Protein"]
    fat = food["Fat"]
    carbs = food["Carbohydrates"]

    # Recommendation logic
    recommendation = ""

    if goal == "weight_loss":

        if calories > 400:
            recommendation = "Not ideal for weight loss"
        else:
            recommendation = "Good for weight loss"

    elif goal == "muscle_gain":

        if protein > 20:
            recommendation = "Excellent for muscle gain"
        else:
            recommendation = "Add more protein"

    else:

        recommendation = "Balanced food option"

    return {
        "food": food_name,
        "calories": calories,
        "protein": protein,
        "fat": fat,
        "carbs": carbs,
        "recommendation": recommendation
    }