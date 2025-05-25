"""Convert Kubernetes quantity strings and pretty-print values.

이 모듈은 Kubernetes의 리소스 수량 문자열(예: '100Mi', '200m')을
실제 숫자 값(바이트, CPU 코어)으로 변환하고, 이를 사람이 읽기 쉬운
형식으로 포맷팅하는 유틸리티 함수들을 제공합니다.
"""

import re
from typing import Union

# 단위 변환 상수
_KI = 1024
_MEM = {"Ki": _KI, "Mi": _KI**2, "Gi": _KI**3, "Ti": _KI**4}
_CPU = {"n": 1e-9, "u": 1e-6, "m": 1e-3, "": 1}

# 수량 문자열 파싱을 위한 정규식
_QUANTITY_RE = re.compile(r"^\s*([0-9.]+)\s*([a-zA-Z]*)\s*$")


def _convert(raw: Union[str, int, float], table: dict[str, float]) -> float:
    """K8s quantity → float (bytes or cores).

    Kubernetes 수량 문자열을 실제 숫자 값으로 변환합니다.

    Args:
        raw (Union[str, int, float]): 변환할 값 (예: '128974848Ki', '250m')
        table (dict[str, float]): 단위 변환 테이블 (_MEM 또는 _CPU)

    Returns:
        float: 변환된 값 (바이트 또는 코어)

    Raises:
        ValueError: 입력값이 None이거나 형식이 잘못된 경우
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
    """메모리 quantity → bytes

    Kubernetes 메모리 수량 문자열을 바이트로 변환합니다.

    Args:
        q (Union[str, int, float]): 변환할 메모리 값 (예: '128Mi', '1Gi')

    Returns:
        float: 바이트 단위로 변환된 값

    Examples:
        >>> mem_to_bytes('128Mi')
        134217728.0
        >>> mem_to_bytes('1Gi')
        1073741824.0
    """
    return _convert(q, _MEM)


def cpu_to_cores(q: Union[str, int, float]) -> float:
    """CPU quantity → cores

    Kubernetes CPU 수량 문자열을 코어 수로 변환합니다.

    Args:
        q (Union[str, int, float]): 변환할 CPU 값 (예: '500m', '2')

    Returns:
        float: 코어 단위로 변환된 값

    Examples:
        >>> cpu_to_cores('500m')
        0.5
        >>> cpu_to_cores('2')
        2.0
    """
    return _convert(q, _CPU)


# pretty-print helpers -------------------------------------------------------
def fmt_bytes_gib(num_bytes: Union[str, int, float]) -> str:
    """Bytes → GiB 문자열 (소수점 2자리)

    바이트 값을 GiB 단위의 문자열로 변환합니다.

    Args:
        num_bytes (Union[str, int, float]): 바이트 값

    Returns:
        str: 'x.xx GiB' 형식의 문자열

    Examples:
        >>> fmt_bytes_gib(1073741824)
        '1.00 GiB'
    """
    num = float(num_bytes)
    return f"{num / (1024 ** 3):.2f} GiB"


def fmt_cores(cores: Union[str, int, float]) -> str:
    """cores 실수 → 'x.xx cores'

    CPU 코어 값을 포맷팅된 문자열로 변환합니다.

    Args:
        cores (Union[str, int, float]): 코어 값

    Returns:
        str: 'x.xx cores' 형식의 문자열

    Examples:
        >>> fmt_cores(0.5)
        '0.50 cores'
    """
    return f"{float(cores):.2f} cores"
