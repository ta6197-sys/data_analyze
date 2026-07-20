"""
Day1 종합 실습: 데이터 수집 미니 파이프라인

작성자: 김태림 (광주 4반)
작성일: 2026-07-21

프로그램 개요
    Open-Meteo(서울 날씨) · countries.dev(한국 정보) · ip-api(IP 지역정보)
    3개 API를 asyncio + httpx로 동시에 수집한 뒤, Pydantic v2로 필요한
    필드만 검증하고, 검증을 통과한 데이터를 CSV·Parquet 두 형식으로 저장해
    읽기/쓰기 성능을 비교한다. 개별 API 수집·검증 실패는 해당 항목만
    건너뛰고 나머지는 계속 진행한다.

변경 이력
    v1.0 (2026-07-21) 최초 작성
"""
from __future__ import annotations

import asyncio
import logging
from pathlib import Path

from pydantic import ValidationError

from collector import collect_raw, parse_country, parse_ip, parse_weather
from storage import save_and_compare

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)

OUTPUT_DIR = Path(__file__).parent.parent / "output"

# key -> raw dict를 검증된 레코드 리스트로 바꾸는 파서
PARSERS = {
    "weather": parse_weather,
    "country": lambda raw: [parse_country(raw)],
    "ip": lambda raw: [parse_ip(raw)],
}


def main() -> None:
    """3개 API를 수집→검증→저장→성능비교까지 실행한다."""
    OUTPUT_DIR.mkdir(exist_ok=True)
    raw = asyncio.run(collect_raw())

    results = []
    for key, parser in PARSERS.items():
        if raw[key] is None:
            print(f"[{key}] 수집 실패로 건너뜀")
            continue
        try:
            records = parser(raw[key])
        except ValidationError as e:
            logger.error(f"{key} 검증 실패: {e}")
            continue

        results.append(save_and_compare(records, key, OUTPUT_DIR))
        print(f"[{key}] {len(records)}건 검증 통과")

    print("\n=== 저장/성능 비교 결과 ===")
    for r in results:
        print(
            f"{r['name']:8s} rows={r['rows']:>3} | "
            f"CSV     write={r['csv_write_sec'] * 1000:6.2f}ms  read={r['csv_read_sec'] * 1000:6.2f}ms | "
            f"Parquet write={r['parquet_write_sec'] * 1000:6.2f}ms  read={r['parquet_read_sec'] * 1000:6.2f}ms"
        )


if __name__ == "__main__":
    main()
