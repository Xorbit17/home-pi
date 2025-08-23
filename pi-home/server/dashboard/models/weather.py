from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


#Models a weather card on the dashboard for viewing; derived data
class Location(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.FloatField()
    longitude = models.FloatField()

    class Meta:
        indexes = [models.Index(fields=["latitude", "longitude"])]

    def __str__(self): return self.name
class Forecast(models.Model):
    class Icon(models.TextChoices):
        SUNNY = "sunny", "Sunny"
        PARTLY_CLOUDY = "partly_cloudy", "Partly cloudy"
        CLOUDY = "cloudy", "Cloudy"
        RAIN = "rain", "Rain"
        SHOWERS = "showers", "Showers"
        THUNDER = "thunder", "Thunder"
        FOG = "fog", "Fog"
        SNOW = "snow", "Snow"
        WINDY = "windy", "Windy"
    class WindDir(models.TextChoices):
        N = "N"
        NO = "NO"
        O = "O"
        ZO = "ZO"
        Z = "Z"
        ZW = "ZW"
        W = "W"
        NW = "NW"

    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    at = models.DateTimeField(db_index=True)
    generated_at = models.DateField(db_index=True)
    time_label = models.TextField(max_length=100)
    icon_main = models.CharField(max_length=20, choices=Icon.choices,default=Icon.SUNNY)
    icon_transition = models.CharField(max_length=20, choices=Icon.choices, null=True)
    temperature_c = models.DecimalField(
        max_digits=4, decimal_places=1
    )  # e.g. -12.5 .. 38.4
    precip_prob = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )  # 0..100 (%)
    wind_bft = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(12)]
    )  # Beaufort 0..12
    wind_dir = models.CharField(max_length=2,choices=WindDir.choices,default=WindDir.N)

class WeatherSample(models.Model):
    """
    One timeslot per location with raw, unit-consistent values.
    Typically 1-hourly for ALARO.
    """
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    valid_time = models.DateTimeField(db_index=True)  # aware UTC
    # Units: keep these stable
    temperature_c = models.DecimalField(max_digits=5, decimal_places=2)   # e.g. 21.37
    precip_mm = models.DecimalField(max_digits=6, decimal_places=2)       # hourly total (mm)
    wind_ms = models.DecimalField(max_digits=5, decimal_places=2)         # m/s at 10m
    wind_gust_ms = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    cloud_cover_pct = models.PositiveSmallIntegerField(                   # 0..100, if available
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    # room for more (dew point, RH, MSLP, etc.)
    rh_pct = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        null=True, blank=True
    )
    mslp_hpa = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True)

    class Meta:
        unique_together = ("location", "valid_time")
        indexes = [
            models.Index(fields=["location", "valid_time"]),
        ]
        ordering = ["location", "valid_time"]

    def __str__(self):
        return f"{self.location} {self.valid_time:%Y-%m-%d %H:%MZ}"