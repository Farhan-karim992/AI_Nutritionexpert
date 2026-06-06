from django.urls import path
from . import views

urlpatterns = [

    path('profile/', views.profile_setup, name='profile'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('ai-chat/', views.ai_chat, name='ai_chat'),

    path(
        'export-diet-pdf/',
        views.export_diet_pdf,
        name='export_diet_pdf'
    ),

    path(
        'analyze-food-image/',
        views.analyze_food_image,
        name='analyze_food_image'
    ),

    path(
        'ml-predict/',
        views.ml_predict,
        name='ml_predict'
    ),

    path(
        'predict-nutrition/',
        views.predict_nutrition,
        name='predict_nutrition'
    ),

    path(
        'diet-plan/',
        views.diet_plan,
        name='diet_plan'
    ),

    path(
        'food-analysis/',
        views.food_analysis,
        name='food_analysis'
    ),

    path(
        'nutrition-chatbot/',
        views.nutrition_chatbot,
        name='nutrition_chatbot'
    ),
]