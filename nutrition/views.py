from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from openai import OpenAI
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from datetime import datetime
from django.http import HttpResponse
import re

client = OpenAI(api_key=settings.OPENAI_API_KEY)

@csrf_exempt
def ai_chat(request):
    if request.method != "POST":
        return JsonResponse({"reply": "Invalid request"})

    user_message = request.POST.get("message")
    if not user_message:
        return JsonResponse({"reply": "Please enter a message."})

    if "chat_history" not in request.session:
        request.session["chat_history"] = []

    request.session["chat_history"].append({
        "role": "user",
        "content": user_message
    })

    user = request.user
    profile = Profile.objects.filter(user=user).first()

    user_name = user.username if user.is_authenticated else "User"

    if profile:
        user_goal = profile.get_goal_display()
        age = profile.age
        height = profile.height
        weight = profile.weight
    else:
        user_goal = "a healthy lifestyle"
        age = "unknown"
        height = "unknown"
        weight = "unknown"

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
- End with this EXACT block:

NUTRITION_SUMMARY_JSON
{{"calories":1800,"protein":110,"fats":55}}
END_NUTRITION_SUMMARY_JSON
"""
        }
    ] + request.session["chat_history"]

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages
        )

        reply = response.choices[0].message.content

        # ===== Extract nutrition summary =====
        summary_match = re.search(
            r"NUTRITION_SUMMARY_JSON\s*(\{.*?\})\s*END_NUTRITION_SUMMARY_JSON",
            reply,
            re.DOTALL
        )

        if summary_match:
            import json
            try:
                request.session["nutrition_summary"] = json.loads(summary_match.group(1))
            except:
                request.session["nutrition_summary"] = {
                    "calories": "N/A",
                    "protein": "N/A",
                    "fats": "N/A"
                }

        # Remove JSON from visible reply
        reply = re.sub(
            r"NUTRITION_SUMMARY_JSON.*?END_NUTRITION_SUMMARY_JSON",
            "",
            reply,
            flags=re.DOTALL
        ).strip()

        request.session["chat_history"].append({
            "role": "assistant",
            "content": reply
        })

        request.session["chat_history"] = request.session["chat_history"][-10:]
        request.session.modified = True

        if "diet plan" in user_message.lower():
            request.session["latest_diet_plan"] = reply

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
def dashboard(request):
    profile = Profile.objects.filter(user=request.user).first()
    return render(request, 'nutrition/main_dashboard.html', {
        'profile': profile
    })
@login_required
def export_diet_pdf(request):
    diet_plan = request.session.get("latest_diet_plan")
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



    if not diet_plan:
        return HttpResponse("No diet plan available.")

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