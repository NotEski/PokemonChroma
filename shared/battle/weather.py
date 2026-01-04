from pydantic import BaseModel
from enum import Enum

class BattleWeather(Enum):
    HARSH_SUNLIGHT = "harsh_sunlight"
    RAIN = "rain"
    SANDSTORM = "sandstorm"
    HAIL = "hail"
    SNOW = "snow"
    FOG = "fog"
    EXTREMELY_HARSH_SUNLIGHT = "extremely_harsh_sunlight"
    HEAVY_RAIN = "heavy_rain"
    STRONG_WIND = "strong_wind"
    SHADOWY_AURA = "shadowy_aura"
    NONE = None

class WeatherTurns(BaseModel):
    weather: BattleWeather
    remaining_turns: int

