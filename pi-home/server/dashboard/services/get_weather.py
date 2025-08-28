import re
import requests

from dashboard.constants import OPENWEATHERMAP_KEY
import datetime as python_datetime
from django.utils.timezone import make_aware
from typing import List, Optional, Iterable, Tuple
from pydantic import BaseModel, ValidationError


class WeatherItem(BaseModel):
    id: int
    main: str
    description: str
    icon: str

class CurrentModel(BaseModel):
    dt: int
    sunrise: int
    sunset: int
    temp: float
    feels_like: float
    pressure: int
    humidity: int
    dew_point: float
    uvi: float
    clouds: int # %
    visibility: int
    wind_speed: float
    wind_deg: int
    wind_gust: float
    weather: List[WeatherItem]


class TempModel(BaseModel):
    day: float
    min: float
    max: float
    night: float
    eve: float
    morn: float


class FeelsLikeModel(BaseModel):
    day: float
    night: float
    eve: float
    morn: float


class DailyItem(BaseModel):
    dt: int
    sunrise: int
    sunset: int
    moonrise: int
    moonset: int
    moon_phase: float
    summary: Optional[str] = ""  # 'summary' isn't always present in official responses
    temp: TempModel
    feels_like: FeelsLikeModel
    pressure: int
    humidity: int
    dew_point: float
    wind_speed: float
    wind_deg: int
    wind_gust: float
    weather: List[WeatherItem]
    clouds: int
    pop: float  # Probability of precipitation (0–100)
    rain: Optional[float] = None
    snow: Optional[float] = None
    uvi: float


class OneCallResponse(BaseModel):
    lat: float
    lon: float
    timezone: str
    timezone_offset: int
    current: CurrentModel
    daily: List[DailyItem]



def dms_to_decimal(dms_str):
    """
    Converts a DMS string (e.g. 51°18'15.5\"N) to decimal degrees as float.
    """
    pattern = re.compile(
        r"""(?P<degrees>\d+)[°\s]+(?P<minutes>\d+)[\'\s]+(?P<seconds>\d+(?:\.\d+)?)[\"\s]*(?P<direction>[NSEW])""",
        re.VERBOSE,
    )

    match = pattern.match(dms_str.strip())
    if not match:
        raise ValueError(f"Invalid DMS coordinate: {dms_str}")

    deg = float(match.group("degrees"))
    minutes = float(match.group("minutes"))
    sec = float(match.group("seconds"))
    direction = match.group("direction")

    decimal = deg + minutes / 60 + sec / 3600
    if direction in ("S", "W"):
        decimal = -decimal

    return decimal


def convert_lat_lon(lat_str, lon_str):
    """
    Returns a tuple (latitude, longitude) in decimal degrees
    from DMS strings.
    """
    return dms_to_decimal(lat_str), dms_to_decimal(lon_str)


class OpenWeatherError(RuntimeError):
    pass

def fetch_weather(
    lat: float,
    lon: float,
    api_key: str,
    exclude: Optional[Iterable[str]] = None,
    units: str = "metric",
    lang: str = "en",
    timeout: float = 10.0,
) -> OneCallResponse:
    url = "https://api.openweathermap.org/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": api_key,
        "units": units,
        "lang": lang,
    }

    if exclude:
        excl = {"hourly", *map(str.strip, exclude)}
        params["exclude"] = ",".join(sorted(excl))

    try:
        resp = requests.get(url, params=params, timeout=timeout)
    except requests.RequestException as e:
        raise OpenWeatherError(f"Network error talking to OpenWeather: {e}") from e

    if resp.status_code == 401:
        raise OpenWeatherError("Unauthorized (401): check your API key.")
    if resp.status_code == 429:
        raise OpenWeatherError("Rate limited (429): too many requests.")
    # TODO: raise for other 4xx/5xx?
    resp.raise_for_status()
    json = resp.json()

    try:
        return OneCallResponse.model_validate(json)
    except ValidationError as ve:
        raise OpenWeatherError(f"Response validation failed: {ve}") from ve

def get_weather(location: Tuple[str,str]):
    lat,lon = convert_lat_lon(*location)
    api_key = OPENWEATHERMAP_KEY
    return fetch_weather(lat,lon,api_key)




    


    

