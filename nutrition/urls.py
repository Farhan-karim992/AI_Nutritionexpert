from django.urls import path
from .views import profile_setup, dashboard
from .views import ai_chat
from .views import export_diet_pdf

urlpatterns = [
    path('profile/', profile_setup, name='profile'),
    path('dashboard/', dashboard, name='dashboard'),
    path('ai-chat/', ai_chat, name='ai_chat'),
    path("export-diet-pdf/", export_diet_pdf, name="export_diet_pdf"),
]
