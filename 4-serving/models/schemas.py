from pydantic import BaseModel
from typing import Optional, Generic, TypeVar, Dict, Any

T = TypeVar("T")

class ProvinceWeatherRecord(BaseModel):
    province: str
    temp: float
    humidity: int
    description: str
    lat: float
    lon: float
    timestamp: str
    rain_1h: float = 0.0

class WeatherSummary(BaseModel):
    avg_temp: float
    max_temp_val: float
    max_temp_province: str
    min_temp_val: float
    min_temp_province: str
    total_records: int
    mapreduce_time: int
    spark_time: int
    max_rain_val: float = 0.0
    max_rain_province: str = "N/A"

class HealthStatus(BaseModel):
    status: str
    timestamp: str
    data_source: str
    records: Dict[str, int]

class ApiResponse(BaseModel, Generic[T]):
    success: bool
    data: T
    count: Optional[int] = None
    timestamp: str
    message: str
