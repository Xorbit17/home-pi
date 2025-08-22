from django.shortcuts import render
from .models import Forecast

def home(request):
    return render(request, "dashboard/home.html", {"msg": "Hello from Django templates"})

def forecast(request):
    forecasts = Forecast.objects.all()[:24]  # cap for now
    return render(request, "dashboard/forecast.html", {"forecasts": forecasts})

def news(request):
    return render(request, "dashboard/news.html")
