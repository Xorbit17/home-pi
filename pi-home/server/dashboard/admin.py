from django.contrib import admin
from models.weather import Forecast

@admin.register(Forecast)
class ForecastAdmin(admin.ModelAdmin):
    list_display = ("location", "at", "icon", "temperature_c", "precip_prob", "wind_bft")
    list_filter = ("location", "icon")
    search_fields = ("location",)
    ordering = ("at",)