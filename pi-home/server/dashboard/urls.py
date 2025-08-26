from django.urls import path
from .views import home, photo, dashboard

urlpatterns = [
    path("", home, name="home"),  # matches "/"
    path("dashboard", dashboard, name="dashboard"),
    # path("forecast", forecast, name="forecast"),
    # path("news", news, name="news"),
    path("photo", photo, name="photo"),
]
