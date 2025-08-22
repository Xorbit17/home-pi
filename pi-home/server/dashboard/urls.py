from django.urls import path
from .views import home, forecast, news

urlpatterns = [
    path("", home, name="home"),  # matches "/"
    path("forecast", forecast, name="forecast"),
    path("news", news, name="news"),
]
