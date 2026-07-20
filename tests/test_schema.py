"""schemas.py의 Pydantic 모델 검증 테스트."""
import pytest
from pydantic import ValidationError

from schemas import CountryInfo, IpInfo, WeatherRecord


def test_weather_record_valid():
    record = WeatherRecord(time="2026-07-21T00:00", temperature_2m=24.9, precipitation_probability=90)
    assert record.precipitation_probability == 90


def test_weather_record_invalid_probability_raises():
    with pytest.raises(ValidationError):
        WeatherRecord(time="2026-07-21T00:00", temperature_2m=24.9, precipitation_probability=150)


def test_country_info_valid():
    country = CountryInfo(
        name="Korea (Republic of)",
        capital="Seoul",
        region="Asia",
        area=100210,
        population=51780579,
        latlng=[37, 127.5],
    )
    assert country.capital == "Seoul"


def test_country_info_invalid_area_raises():
    with pytest.raises(ValidationError):
        CountryInfo(
            name="Korea (Republic of)",
            capital="Seoul",
            region="Asia",
            area=-1,
            population=51780579,
            latlng=[37, 127.5],
        )


def test_ip_info_valid():
    ip_info = IpInfo(
        query="8.8.8.8", country="United States", city="Ashburn",
        lat=39.03, lon=-77.5, timezone="America/New_York",
    )
    assert ip_info.query == "8.8.8.8"


def test_ip_info_missing_city_raises():
    with pytest.raises(ValidationError):
        IpInfo(query="8.8.8.8", country="United States", city="", lat=39.03, lon=-77.5, timezone="America/New_York")
