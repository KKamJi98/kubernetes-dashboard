"""Convert Kubernetes quantity strings and pretty-print values.

This module provides utilities for converting Kubernetes resource quantity strings
(like '100m' for CPU or '1Gi' for memory) to standard numeric values and formatting
them for display in the dashboard.

Kubernetes uses a specific format for resource quantities:
- CPU: '100m' = 0.1 cores, '1' = 1 core
- Memory: '1Ki' = 1024 bytes, '1Mi' = 1024^2 bytes, '1Gi' = 1024^3 bytes

References:
- https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/apimachinery/pkg/api/resource/quantity.go
"""

import re
from typing import Union

# Constants for unit conversions
_KI = 1024  # Binary unit base (2^10)
_MEM = {"Ki": _KI, "Mi": _KI**2, "Gi": _KI**3, "Ti": _KI**4}  # Memory unit multipliers
_CPU = {"n": 1e-9, "u": 1e-6, "m": 1e-3, "": 1}  # CPU unit multipliers

# Regular expression to parse quantity strings like '100m', '1Gi'
_QUANTITY_RE = re.compile(r"^\s*([0-9.]+)\s*([a-zA-Z]*)\s*$")


def _convert(raw: Union[str, int, float], table: dict[str, float]) -> float:
    """Convert Kubernetes quantity string to float value (bytes or cores).

    Args:
        raw: A string like '128974848Ki', '250m', or numeric value already in base unit
        table: Conversion table mapping units to their multipliers

    Returns:
        Float value in the base unit (bytes for memory, cores for CPU)

    Raises:
        ValueError: If the quantity format is invalid or None
    """
    # If already a numeric type, return as float
    if isinstance(raw, (int, float)):
        return float(raw)

    if raw is None:
        raise ValueError("Quantity is None")

    # Parse the quantity string using regex
    match = _QUANTITY_RE.match(str(raw))
    if not match:
        raise ValueError(f"Invalid quantity format: {raw!r}")

    # Extract numeric value and unit
    num, unit = match.groups()
    # Convert using the appropriate multiplier from the table
    return float(num) * table.get(unit, 1)


# Public helper functions -------------------------------------------------------------
def mem_to_bytes(q: Union[str, int, float]) -> float:
    """Convert memory quantity to bytes.
    
    Args:
        q: Memory quantity string (e.g., '1Gi', '512Mi') or numeric value in bytes
        
    Returns:
        Memory value in bytes as a float
    """
    return _convert(q, _MEM)


def cpu_to_cores(q: Union[str, int, float]) -> float:
    """Convert CPU quantity to cores.
    
    Args:
        q: CPU quantity string (e.g., '100m', '0.5') or numeric value in cores
        
    Returns:
        CPU value in cores as a float
    """
    return _convert(q, _CPU)


# Pretty-print helper functions -------------------------------------------------------
def fmt_bytes_gib(num_bytes: Union[str, int, float]) -> str:
    """Format bytes value to GiB string with 2 decimal places.
    
    Args:
        num_bytes: Bytes value as number or string
        
    Returns:
        Formatted string like '1.50 GiB'
    """
    num = float(num_bytes)
    return f"{num / (1024 ** 3):.2f} GiB"


def fmt_cores(cores: Union[str, int, float]) -> str:
    """Format cores value to string with 2 decimal places.
    
    Args:
        cores: CPU cores as number or string
        
    Returns:
        Formatted string like '0.50 cores'
    """
    return f"{float(cores):.2f} cores"
