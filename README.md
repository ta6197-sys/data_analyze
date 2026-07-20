# 과제3 — 데이터 수집 미니 파이프라인 [Day 1] 종합 실습

> 원문: 123.pdf p.64~67

## 개요
앞의 실습1·2보다 규모가 큰 **종합 실습**입니다. 비동기 API 수집 → Pydantic 검증 → 저장/성능비교 → 테스트/린트/Git 커밋까지 전체 파이프라인을 구축합니다. 채점 총점 100점, 제출 기한 엄수가 중요합니다.

## 사용 API (3개, 동시 수집 대상)
| API | 용도 | URL |
|---|---|---|
| Open-Meteo | 서울 3일 시간대별 기온·강수확률 | `https://api.open-meteo.com/v1/forecast?latitude=37.5665&longitude=126.9780&hourly=temperature_2m,precipitation_probability&forecast_days=3&timezone=Asia/Seoul` |
| Countries.dev | 한국 국가 정보 | `https://countries.dev/alpha/KOR` (또는 restcountries류 대체 API 확인 필요) |
| ip-api | IP 기반 지역 정보 | `http://ip-api.com/json/8.8.8.8` |

> ⚠️ PDF에 있는 Open-Meteo URL은 `api.openmeteo.com`으로 오탈자가 있을 수 있습니다. 실제 정식 도메인은 `api.open-meteo.com` 입니다. 실행 전 브라우저에서 직접 URL을 열어 응답이 정상인지 먼저 확인하세요. `countries.dev`도 실제 서비스 존재 여부를 확인해보고, 안 되면 `restcountries.com/v3.1/alpha/KOR` 등 대체 API로 바꿔도 무방합니다 (강사에게 확인 권장).

## 준비 단계

### 1. 환경 준비
```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```
`requirements.txt` 예시:
```
httpx
pydantic
pandas
pyarrow
pytest
ruff
```
```powershell
pip install -r requirements.txt
```

### 2. 비동기 수집 — `asyncio` + `httpx` + `asyncio.gather()`
- 3개 API를 각각 `async def fetch_xxx(client)` 함수로 분리
- `asyncio.gather()`로 동시 실행
```python
import asyncio
import httpx

async def fetch_weather(client: httpx.AsyncClient) -> dict:
    r = await client.get("https://api.open-meteo.com/v1/forecast", params={
        "latitude": 37.5665, "longitude": 126.9780,
        "hourly": "temperature_2m,precipitation_probability",
        "forecast_days": 3, "timezone": "Asia/Seoul",
    })
    r.raise_for_status()
    return r.json()

async def fetch_country(client): ...
async def fetch_ip(client): ...

async def collect_all():
    async with httpx.AsyncClient(timeout=10) as client:
        return await asyncio.gather(
            fetch_weather(client), fetch_country(client), fetch_ip(client),
            return_exceptions=True,  # 하나 실패해도 나머지는 계속
        )
```

### 3. 스키마 검증 — Pydantic v2
- 각 API 응답에서 필요한 필드만 뽑아 Pydantic 모델로 정의 (예: `WeatherRecord`, `CountryInfo`, `IpInfo`)
- 타입/범위 검증 실패 시 `ValidationError`를 잡아 로그 남기고 계속 진행 (전체 파이프라인이 죽지 않도록)

### 4. 저장 및 성능 비교 — CSV vs Parquet
```python
import time
import pandas as pd

df = pd.DataFrame([r.model_dump() for r in valid_records])

t0 = time.perf_counter()
df.to_csv("output.csv", index=False)
csv_write = time.perf_counter() - t0

t0 = time.perf_counter()
df.to_parquet("output.parquet")
parquet_write = time.perf_counter() - t0

t0 = time.perf_counter()
pd.read_csv("output.csv")
csv_read = time.perf_counter() - t0

t0 = time.perf_counter()
pd.read_parquet("output.parquet")
parquet_read = time.perf_counter() - t0

print(f"CSV write={csv_write:.4f}s read={csv_read:.4f}s")
print(f"Parquet write={parquet_write:.4f}s read={parquet_read:.4f}s")
```

### 5. 테스트 & 린트 & Git
- `tests/test_schema.py`에 Pydantic 모델 검증 테스트 1건 이상 작성
```python
import pytest
from pydantic import ValidationError
from mymodule import WeatherRecord

def test_invalid_temperature_raises():
    with pytest.raises(ValidationError):
        WeatherRecord(temperature=-999, time="2026-07-20T00:00")
```
- `pytest` 실행 → 통과 확인
- `ruff check .` 실행 → 오류 0건까지 정리
- Git 초기화 및 커밋 (이 폴더가 아직 git repo가 아니므로 `git init` 필요)
```powershell
git init
git add .
git commit -m "Day1 종합실습: 비동기 수집 파이프라인 구현"
```

## 전체 진행 순서 (권장)
1. venv + requirements.txt 세팅
2. API 3개 개별로 먼저 `httpx.get()` (동기)으로 응답 확인 → 필드 구조 파악
3. Pydantic 모델 정의 (확인한 필드 기준)
4. 비동기 함수로 전환 + `asyncio.gather()`로 묶기
5. 검증 파이프라인 연결 (수집 → 검증 → valid/invalid 분리)
6. CSV/Parquet 저장 + 성능 비교 출력
7. pytest 테스트 작성 → 통과 확인
8. ruff 검사 → 정리
9. git 커밋
10. 실행 결과 캡처 + 의견 정리 (PDF로 별도 제출)

## 제출물 (별도 유의!)
1. **코드**: 폴더 전체 → `캠퍼스명_반_이름_실습명.zip` (예: `서울_1반_홍길동_day1종합실습.zip`)
   - Github에 올린 뒤 해당 폴더 구조 그대로 다운받아 압축해도 됨
2. **실행결과 정리 (PDF)**: 실행 화면 캡처 + 코드 분석에 대한 본인 의견(개선점, 코드 품질 측면 등)
3. **제출 기한**: 1차 — Day1 과정 종료 전, 2차 — Day2 시작 1시간 전. **기한 초과 시 감점**

## 권장 폴더 구조
```
day1_pipeline/
├── venv/
├── requirements.txt
├── src/
│   ├── collector.py     # asyncio + httpx 수집
│   ├── schemas.py       # Pydantic 모델
│   └── storage.py       # CSV/Parquet 저장 + 성능비교
├── tests/
│   └── test_schema.py
├── output.csv
├── output.parquet
└── README.md            # 실행 방법 + 결과 요약
```
