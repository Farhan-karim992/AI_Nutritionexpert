from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from datetime import datetime
from django.http import HttpResponse
import re
import base64
from django.views.decorators.csrf import csrf_exempt
import joblib
import numpy as np

from .food_engine import analyze_food
from .chatbot_engine import analyze_sentence


model = joblib.load("nutrition_model.pkl")
@login_required
def ml_predict(request):

    protein = float(request.GET.get("protein"))
    fat = float(request.GET.get("fat"))
    carbs = float(request.GET.get("carbs"))

    data = np.array([[protein, fat, carbs]])

    prediction = model.predict(data)[0]

    return JsonResponse({
        "prediction": round(prediction, 2)
    })
@csrf_exempt
def ai_chat(request):

    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request"})

    user_message = request.POST.get("message")

    if not user_message:
        return JsonResponse({"reply": "Please enter a message."})

    # Create chat history
    if "chat_history" not in request.session:
        request.session["chat_history"] = []

    # Save user message
    request.session["chat_history"].append({
        "role": "user",
        "content": user_message
    })

    # Get user profile
    user = request.user
    profile = Profile.objects.filter(user=user).first()

    user_name = user.username if user.is_authenticated else "User"

    if profile:
        user_goal = profile.get_goal_display()
        age = profile.age
        height = profile.height
        weight = profile.weight
    else:
        user_goal = "healthy lifestyle"
        age = "unknown"
        height = "unknown"
        weight = "unknown"

    # AI instructions
    messages = [
        {
            "role": "system",
            "content": f"""
You are WellnessAI, a friendly AI-powered nutrition assistant.

User profile:
Name: {user_name}
Age: {age}
Height: {height} cm
Weight: {weight} kg
Goal: {user_goal}

Instructions:
- Remember previous messages
- Be consistent
- Avoid medical diagnosis
- Use simple formatting
- Generate clean diet plans

End responses with this EXACT block:

NUTRITION_SUMMARY_JSON
{{"calories":1800,"protein":110,"fats":55}}
END_NUTRITION_SUMMARY_JSON
"""
        }
    ] + request.session["chat_history"]

    try:

        prompt = ""

        for msg in messages:
            role = msg["role"]
            content = msg["content"]

            prompt += f"{role}: {content}\n"

        response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=prompt
)

        reply = response.text

        # Extract nutrition summary
        summary_match = re.search(
            r"NUTRITION_SUMMARY_JSON\s*(\{.*?\})\s*END_NUTRITION_SUMMARY_JSON",
            reply,
            re.DOTALL
        )

        if summary_match:

            import json

            try:
                request.session["nutrition_summary"] = json.loads(
                    summary_match.group(1)
                )

            except:
                request.session["nutrition_summary"] = {
                    "calories": "N/A",
                    "protein": "N/A",
                    "fats": "N/A"
                }

        # Remove JSON from visible response
        reply = re.sub(
            r"NUTRITION_SUMMARY_JSON.*?END_NUTRITION_SUMMARY_JSON",
            "",
            reply,
            flags=re.DOTALL
        ).strip()

        # Save AI reply
        request.session["chat_history"].append({
            "role": "assistant",
            "content": reply
        })

        # Keep last 10 messages
        request.session["chat_history"] = request.session["chat_history"][-10:]

        request.session.modified = True

        # Save latest diet plan
        if "diet plan" in user_message.lower():
            request.session["latest_diet_plan"] = reply

        return JsonResponse({"reply": reply})

    except Exception as e:
        return JsonResponse({"reply": f"Error: {str(e)}"})
@csrf_exempt
@login_required
def analyze_food_image(request):

    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request"})

    image = request.FILES.get("image")

    if not image:
        return JsonResponse({"reply": "No image uploaded"})

    try:

        reply = """
Detected Food:
- Rice
- Chicken
- Salad

Estimated Calories: 650 kcal
Protein: 35 g
Fats: 18 g
"""

        return JsonResponse({"reply": reply})

    except Exception as e:
        return JsonResponse({"reply": f"Error: {str(e)}"})
@login_required
def profile_setup(request):
    profile = Profile.objects.filter(user=request.user).first()

    if request.method == 'POST':
        age = request.POST.get('age')
        height = request.POST.get('height')
        weight = request.POST.get('weight')
        goal = request.POST.get('goal')

        if profile:
            profile.age = age
            profile.height = height
            profile.weight = weight
            profile.goal = goal
            profile.save()
        else:
            Profile.objects.create(
                user=request.user,
                age=age,
                height=height,
                weight=weight,
                goal=goal
            )

        # 🔥 redirect to MAIN dashboard
        return redirect('dashboard')

    return render(request, 'nutrition/profile_setup.html', {
        'profile': profile
    })

@login_required
def nutrition_chatbot(request):

    reply = ""
    user_message = ""

    if request.method == "POST":

        user_text = request.POST.get(
            "message"
        )

        profile = Profile.objects.filter(
            user=request.user
        ).first()

        reply = analyze_sentence(
            user_text,
            profile
        )

        user_message = user_text

    return render(
        request,
        "nutrition/chatbot.html",
        {
            "reply": reply,
            "user_message": user_message
        }
    )

@login_required
def dashboard(request):

    profile = Profile.objects.filter(
        user=request.user
    ).first()

    # BMI Calculation
    height_m = profile.height / 100

    bmi = round(
        profile.weight / (height_m ** 2),
        1
    )

    # BMI Status
    if bmi < 18.5:
        bmi_status = "Underweight"

    elif bmi < 25:
        bmi_status = "Normal"

    elif bmi < 30:
        bmi_status = "Overweight"

    else:
        bmi_status = "Obese"

    # Health Score
    health_score = 100

    if bmi > 25:
        health_score -= 20

    if profile.goal == "weight_loss":
        health_score -= 5

    # Personalized nutrition calculation

    if profile.goal == "muscle_gain":

        calories = 2800
        protein = 180
        fats = 80
        carbs = 320

    elif profile.goal == "weight_loss":

        calories = 1800
        protein = 130
        fats = 50
        carbs = 180

    else:

        calories = 2200
        protein = 140
        fats = 65
        carbs = 250

    nutrition_data = {
        "calories": calories,
        "protein": protein,
        "fats": fats,
        "carbs": carbs
    }

    return render(
        request,
        'nutrition/main_dashboard.html',
        {
            'profile': profile,
            'nutrition_data': nutrition_data,
            'bmi': bmi,
            'bmi_status': bmi_status,
            'health_score': health_score
        }
    )
@login_required
def diet_plan(request):

    profile = Profile.objects.filter(
        user=request.user
    ).first()

    if not profile:
        return HttpResponse("Profile not found")

    # Load ML models
    diet_model = joblib.load(
        "diet_model.pkl"
    )

    diet_goal_encoder = joblib.load(
        "diet_goal_encoder.pkl"
    )

    meal_encoder = joblib.load(
        "meal_encoder.pkl"
    )

    diet_recommendation_encoder = joblib.load(
        "diet_recommendation_encoder.pkl"
    )

    # BMI Calculation
    height_m = profile.height / 100

    bmi = round(
        profile.weight / (height_m ** 2),
        1
    )

    # Encode user goal
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

    goal_encoded = (
     diet_goal_encoder.transform(
        [goal]
    )[0]
)

    # ================= BREAKFAST =================

    breakfast_encoded = meal_encoder.transform(
        ["breakfast"]
    )[0]

    breakfast_prediction = diet_model.predict(
        [[
            bmi,
            goal_encoded,
            breakfast_encoded
        ]]
    )

    breakfast = (
        diet_recommendation_encoder
        .inverse_transform(
            breakfast_prediction
        )[0]
    )

    # ================= LUNCH =================

    lunch_encoded = meal_encoder.transform(
        ["lunch"]
    )[0]

    lunch_prediction = diet_model.predict(
        [[
            bmi,
            goal_encoded,
            lunch_encoded
        ]]
    )

    lunch = (
        diet_recommendation_encoder
        .inverse_transform(
            lunch_prediction
        )[0]
    )

    # ================= DINNER =================

    dinner_encoded = meal_encoder.transform(
        ["dinner"]
    )[0]

    dinner_prediction = diet_model.predict(
        [[
            bmi,
            goal_encoded,
            dinner_encoded
        ]]
    )

    dinner = (
        diet_recommendation_encoder
        .inverse_transform(
            dinner_prediction
        )[0]
    )
    breakfast = breakfast.replace("_", ", ").title()

    lunch = lunch.replace("_", ", ").title()

    dinner = dinner.replace("_", ", ").title()
    return render(
        request,
        "nutrition/diet_plan.html",
        {
            "profile": profile,
            "bmi": bmi,
            "breakfast": breakfast,
            "lunch": lunch,
            "dinner": dinner
        }
    )
@login_required
def food_analysis(request):

    food_result = None

    if request.method == "POST":

        food_name = request.POST.get("food")

        profile = Profile.objects.filter(
            user=request.user
        ).first()

        goal = profile.goal if profile else "maintenance"

        food_result = analyze_food(
            food_name,
            goal
        )

    return render(
        request,
        "nutrition/food_analysis.html",
        {
            "food_result": food_result
        }
    )
@login_required
def predict_nutrition(request):

    profile = Profile.objects.filter(user=request.user).first()

    if not profile:
        return HttpResponse("Profile not found")

    # Convert goal into number
    goal_map = {
        "weight_loss": 0,
        "maintenance": 1,
        "muscle_gain": 2
    }

    goal_value = goal_map.get(profile.goal, 1)

    # Input for ML model
    sample = [[
        profile.age,
        profile.height,
        profile.weight,
        goal_value
    ]]

    prediction = model.predict(sample)

    calories = round(prediction[0])

    protein = round(calories * 0.25 / 4)
    fats = round(calories * 0.20 / 9)

    result = f"""
Estimated Daily Nutrition

Calories: {calories} kcal
Protein: {protein} g
Fats: {fats} g
"""

    return HttpResponse(result)
@login_required
def export_diet_pdf(request):
    diet_plan = request.session.get("latest_diet_plan")
    if not diet_plan:
        return HttpResponse("No diet plan available.")
    # ================= EXTRACT NUTRITION SUMMARY =================
    calories = "N/A"
    protein = "N/A"
    fats = "N/A"

    cal_match = re.search(r"(\d{3,4})\s*kcal", diet_plan, re.IGNORECASE)
    prot_match = re.search(r"(\d{2,3})\s*g\s*protein", diet_plan, re.IGNORECASE)
    fat_match = re.search(r"(\d{2,3})\s*g\s*fat", diet_plan, re.IGNORECASE)

    if cal_match:
     calories = cal_match.group(1)

    if prot_match:
     protein = prot_match.group(1)

    if fat_match:
     fats = fat_match.group(1)



    

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="WellnessAI_Nutrition_Plan.pdf"'

    c = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # 🎨 Colors
    primary = HexColor("#2f855a")
    dark = HexColor("#1a202c")
    muted = HexColor("#718096")

    y = height - 60

    # ================= HEADER =================
    c.setFont("Helvetica-Bold", 26)
    c.setFillColor(primary)
    c.drawString(50, y, "WellnessAI")
    y -= 28

    c.setFont("Helvetica", 13)
    c.setFillColor(dark)
    c.drawString(50, y, "Personalized Nutrition & Diet Plan")
    y -= 20

    c.setFont("Helvetica", 10)
    c.setFillColor(muted)
    c.drawString(50, y, f"Generated on: {datetime.now().strftime('%d %B %Y')}")
    y -= 25

    c.line(50, y, width - 50, y)
    y -= 30

    # ================= CLIENT PROFILE =================
    profile = Profile.objects.filter(user=request.user).first()

    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(primary)
    c.drawString(50, y, "Client Profile")
    y -= 18

    c.setFont("Helvetica", 11)
    c.setFillColor(dark)
    c.drawString(50, y, f"Name: {request.user.username}")
    y -= 15

    if profile:
        c.drawString(50, y, f"Goal: {profile.get_goal_display()}")
        y -= 15
        c.drawString(50, y, f"Age: {profile.age} | Height: {profile.height} cm | Weight: {profile.weight} kg")
        y -= 15

    y -= 20
    c.line(50, y, width - 50, y)
    y -= 30
    # ================= NUTRITION SUMMARY BOX =================
    box_top = y
    box_height = 90

    c.setStrokeColor(primary)
    c.setLineWidth(1.5)
    c.rect(50, box_top - box_height, width - 100, box_height)

    c.setFont("Helvetica-Bold", 14)
    c.setFillColor(primary)
    c.drawString(60, box_top - 25, "Daily Nutrition Summary")

    c.setFont("Helvetica", 11)
    c.setFillColor(dark)
    c.drawString(60, box_top - 45, f"Estimated Calories : {calories} kcal")
    c.drawString(60, box_top - 60, f"Protein            : {protein} g")
    c.drawString(60, box_top - 75, f"Fats               : {fats} g")

    y = box_top - box_height - 30
    # ================= DIET PLAN =================
    c.setFont("Helvetica-Bold", 15)
    c.setFillColor(primary)
    c.drawString(50, y, "Daily Meal Plan")
    y -= 25

    c.setFont("Helvetica", 11)
    c.setFillColor(dark)

    for line in diet_plan.split("\n"):
        if y < 80:
            c.showPage()
            y = height - 60
            c.setFont("Helvetica", 11)

        clean_line = line.strip()

        # Section titles
        if clean_line.lower().startswith(("breakfast", "lunch", "dinner", "snack")):
            y -= 10
            c.setFont("Helvetica-Bold", 13)
            c.setFillColor(primary)
            c.drawString(50, y, clean_line.replace(":", ""))
            y -= 18
            c.setFont("Helvetica", 11)
            c.setFillColor(dark)

        elif clean_line:
            c.drawString(65, y, "• " + clean_line)
            y -= 15
        else:
            y -= 8
    
    # ================= NOTES =================
    y -= 20
    c.line(50, y, width - 50, y)
    y -= 25

    c.setFont("Helvetica-Bold", 13)
    c.setFillColor(primary)
    c.drawString(50, y, "Nutritionist Notes")
    y -= 18

    c.setFont("Helvetica", 11)
    c.setFillColor(dark)
    c.drawString(
        50,
        y,
        "Follow this plan consistently, stay hydrated, and adjust portions based on your activity level."
    )

    # ================= FOOTER =================
    c.setFont("Helvetica-Oblique", 9)
    c.setFillColor(muted)
    c.drawString(
        50,
        40,
        "Disclaimer: This plan is AI-generated for educational purposes and does not replace professional medical advice."
    )

    c.showPage()
    c.save()
    return response