"""asyncio + httpx로 3개 API(날씨/국가정보/IP정보)를 동시에 수집한다."""
from __future__ import annotations

import asyncio
import logging

import httpx

from schemas import CountryInfo, IpInfo, WeatherRecord

logger = logging.getLogger(__name__)

WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
WEATHER_PARAMS = {
    "latitude": 37.5665,
    "longitude": 126.9780,
    "hourly": "temperature_2m,precipitation_probability",
    "forecast_days": 3,
    "timezone": "Asia/Seoul",
}
COUNTRY_URL = "https://countries.dev/alpha/KOR"
IP_URL = "http://ip-api.com/json/8.8.8.8"


async def fetch_weather(client: httpx.AsyncClient) -> dict:
    """서울 3일 시간대별 기온·강수확률을 가져온다."""
    response = await client.get(WEATHER_URL, params=WEATHER_PARAMS)
    response.raise_for_status()
    return response.json()


async def fetch_country(client: httpx.AsyncClient) -> dict:
    """한국 국가 정보를 가져온다."""
    response = await client.get(COUNTRY_URL)
    response.raise_for_status()
    return response.json()


async def fetch_ip(client: httpx.AsyncClient) -> dict:
    """IP(8.8.8.8) 기반 지역 정보를 가져온다."""
    response = await client.get(IP_URL)
    response.raise_for_status()
    return response.json()


async def collect_raw() -> dict[str, dict | None]:
    """3개 API를 asyncio.gather()로 동시에 호출한다.

    개별 API가 실패해도 나머지 수집이 막히지 않도록 return_exceptions=True로
    모으고, 실패한 항목은 로그를 남긴 뒤 None으로 채워 반환한다.
    """
    async with httpx.AsyncClient(timeout=10.0) as client:
        results = await asyncio.gather(
            fetch_weather(client),
            fetch_country(client),
            fetch_ip(client),
            return_exceptions=True,
        )

    keys = ("weather", "country", "ip")
    raw: dict[str, dict | None] = {}
    for key, result in zip(keys, results):
        if isinstance(result, Exception):
            logger.error(f"{key} 수집 실패: {result}")
            raw[key] = None
        else:
            logger.info(f"{key} 수집 성공")
            raw[key] = result
    return raw


def parse_weather(raw: dict) -> list[WeatherRecord]:
    """hourly 병렬 배열(time/temperature_2m/precipitation_probability)을 레코드 리스트로 변환한다."""
    hourly = raw["hourly"]
    return [
        WeatherRecord(time=t, temperature_2m=temp, precipitation_probability=prob)
        for t, temp, prob in zip(
            hourly["time"], hourly["temperature_2m"], hourly["precipitation_probability"]
        )
    ]


def parse_country(raw: dict) -> CountryInfo:
    """국가 정보 dict를 CountryInfo로 검증한다."""
    return CountryInfo.model_validate(raw)


def parse_ip(raw: dict) -> IpInfo:
    """IP 정보 dict를 IpInfo로 검증한다."""
    return IpInfo.model_validate(raw)
