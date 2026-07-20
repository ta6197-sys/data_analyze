"""3개 API 응답에서 필요한 필드만 추출해 검증하는 Pydantic v2 모델."""
from __future__ import annotations

from pydantic import BaseModel, Field


class WeatherRecord(BaseModel):
    """Open-Meteo hourly 응답의 한 시간대 데이터."""

    time: str
    temperature_2m: float
    precipitation_probability: int = Field(ge=0, le=100)


class CountryInfo(BaseModel):
    """countries.dev 응답에서 추출한 국가 정보."""

    name: str = Field(min_length=1)
    capital: str = Field(min_length=1)
    region: str = Field(min_length=1)
    area: float = Field(gt=0)
    population: int = Field(gt=0)
    latlng: list[float] = Field(min_length=2, max_length=2)


class IpInfo(BaseModel):
    """ip-api 응답에서 추출한 IP 기반 지역 정보."""

    query: str = Field(min_length=1)
    country: str = Field(min_length=1)
    city: str = Field(min_length=1)
    lat: float
    lon: float
    timezone: str = Field(min_length=1)
