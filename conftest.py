"""tests/ 에서 src/ 안의 모듈을 바로 import할 수 있도록 경로를 추가한다."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))
