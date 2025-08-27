from django.urls import path
from dashboard.views.dashboard import DashboardView
from dashboard.views.home import HomeView
from dashboard.views.photo import PhotoView

urlpatterns = [
    path("", HomeView.as_view(), name="home"),  # matches "/"
    path("dashboard", DashboardView.as_view(), name="dashboard"),
    path("photo", PhotoView.as_view(), name="photo"),
]
