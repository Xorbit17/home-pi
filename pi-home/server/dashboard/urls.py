from django.urls import path
from .views import home, forecast

urlpatterns = [
    path("", home, name="home"),  # matches "/"
    path("forecast", forecast, name="forecase"),
]