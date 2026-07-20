"""검증된 레코드를 CSV/Parquet로 저장하고 읽기·쓰기 시간을 측정해 비교한다."""
from __future__ import annotations

import time
from pathlib import Path

import pandas as pd
from pydantic import BaseModel


def save_and_compare(records: list[BaseModel], name: str, out_dir: Path) -> dict:
    """records를 DataFrame으로 변환해 CSV·Parquet 두 형식으로 저장하고 성능을 비교한다."""
    df = pd.DataFrame([r.model_dump() for r in records])
    csv_path = out_dir / f"{name}.csv"
    parquet_path = out_dir / f"{name}.parquet"

    t0 = time.perf_counter()
    df.to_csv(csv_path, index=False)
    csv_write = time.perf_counter() - t0

    t0 = time.perf_counter()
    df.to_parquet(parquet_path)
    parquet_write = time.perf_counter() - t0

    t0 = time.perf_counter()
    pd.read_csv(csv_path)
    csv_read = time.perf_counter() - t0

    t0 = time.perf_counter()
    pd.read_parquet(parquet_path)
    parquet_read = time.perf_counter() - t0

    return {
        "name": name,
        "rows": len(df),
        "csv_write_sec": csv_write,
        "parquet_write_sec": parquet_write,
        "csv_read_sec": csv_read,
        "parquet_read_sec": parquet_read,
    }
