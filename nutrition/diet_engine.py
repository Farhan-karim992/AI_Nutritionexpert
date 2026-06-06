def generate_diet_plan(goal):

    if goal == "weight_loss":

        return {
            "Breakfast": [
                "Oats",
                "Boiled Eggs",
                "Green Tea"
            ],

            "Lunch": [
                "Grilled Chicken",
                "Brown Rice",
                "Salad"
            ],

            "Dinner": [
                "Soup",
                "Vegetables",
                "Paneer"
            ],

            "Avoid": [
                "Soft Drinks",
                "Fried Food",
                "Sugar"
            ]
        }

    elif goal == "muscle_gain":

        return {
            "Breakfast": [
                "Milk",
                "Banana",
                "Peanut Butter Toast"
            ],

            "Lunch": [
                "Chicken",
                "Rice",
                "Eggs"
            ],

            "Dinner": [
                "Fish",
                "Potatoes",
                "Protein Shake"
            ],

            "Avoid": [
                "Skipping Meals",
                "Junk Food"
            ]
        }

    else:

        return {
            "Breakfast": [
                "Fruits",
                "Eggs",
                "Toast"
            ],

            "Lunch": [
                "Rice",
                "Dal",
                "Vegetables"
            ],

            "Dinner": [
                "Soup",
                "Salad",
                "Chicken"
            ],

            "Avoid": [
                "Excess Sugar",
                "Overeating"
            ]
        }