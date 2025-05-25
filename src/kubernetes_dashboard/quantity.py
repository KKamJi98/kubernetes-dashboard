"""Convert Kubernetes quantity strings and pretty-print values."""
import re
from typing import Union

_KI = 1024
_MEM = {"Ki": _KI, "Mi": _KI**2, "Gi": _KI**3, "Ti": _KI**4}
_CPU = {"n": 1e-9, "u": 1e-6, "m": 1e-3, "": 1}

_QUANTITY_RE = re.compile(r"^\s*([0-9.]+)\s*([a-zA-Z]*)\s*$")

def _convert(raw: Union[str, int, float], table: dict[str, float]) -> float:
    """K8s quantity → float (bytes or cores).

    Accepts str like '128974848Ki', '250m', or numeric types already in base unit.
    """
    # 이미 숫자형이면 그대로 반환
    if isinstance(raw, (int, float)):
        return float(raw)

    if raw is None:
        raise ValueError("Quantity is None")

    match = _QUANTITY_RE.match(str(raw))
    if not match:
        raise ValueError(f"Invalid quantity format: {raw!r}")

    num, unit = match.groups()
    return float(num) * table.get(unit, 1)

# public helpers -------------------------------------------------------------
def mem_to_bytes(q: Union[str, int, float]) -> float:
    """메모리 quantity → bytes"""
    return _convert(q, _MEM)

def cpu_to_cores(q: Union[str, int, float]) -> float:
    """CPU quantity → cores"""
    return _convert(q, _CPU)

# pretty-print helpers -------------------------------------------------------
def fmt_bytes_gib(num_bytes: Union[str, int, float]) -> str:
    """Bytes → GiB 문자열 (소수점 2자리)"""
    num = float(num_bytes)
    return f"{num / (1024 ** 3):.2f} GiB"

def fmt_cores(cores: Union[str, int, float]) -> str:
    """cores 실수 → 'x.xx cores'"""
    return f"{float(cores):.2f} cores"