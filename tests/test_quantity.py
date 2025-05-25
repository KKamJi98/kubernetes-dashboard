"""Tests for the quantity module.

This module contains unit tests for the Kubernetes resource quantity conversion
and formatting functions in the quantity module. It tests:

1. CPU quantity string parsing (e.g., '100m' -> 0.1 cores)
2. Memory quantity string parsing (e.g., '1Gi' -> 1073741824 bytes)
3. CPU cores formatting (e.g., 0.1 -> '0.10 cores')
4. Memory bytes formatting to GiB (e.g., 1073741824 -> '1.00 GiB')

These tests ensure that the quantity conversion functions correctly handle
the Kubernetes resource quantity format and produce the expected results.
"""

import pytest

from kubernetes_dashboard.quantity import (
    cpu_to_cores,
    fmt_bytes_gib,
    fmt_cores,
    mem_to_bytes,
)


def test_cpu_to_cores():
    """Test parsing CPU quantities.
    
    This test verifies that the cpu_to_cores function correctly converts
    Kubernetes CPU quantity strings to floating-point core values.
    
    Test cases:
    - '100m' should convert to 0.1 cores (milli-cores)
    - '1' should convert to 1.0 cores
    - '2.5' should convert to 2.5 cores
    """
    assert cpu_to_cores("100m") == 0.1
    assert cpu_to_cores("1") == 1.0
    assert cpu_to_cores("2.5") == 2.5


def test_mem_to_bytes():
    """Test parsing memory quantities.
    
    This test verifies that the mem_to_bytes function correctly converts
    Kubernetes memory quantity strings to bytes.
    
    Test cases:
    - '1Ki' should convert to 1024 bytes (1 KiB)
    - '1Mi' should convert to 1048576 bytes (1 MiB)
    - '1Gi' should convert to 1073741824 bytes (1 GiB)
    """
    assert mem_to_bytes("1Ki") == 1024
    assert mem_to_bytes("1Mi") == 1024 * 1024
    assert mem_to_bytes("1Gi") == 1024 * 1024 * 1024


def test_fmt_cores():
    """Test formatting CPU cores.
    
    This test verifies that the fmt_cores function correctly formats
    floating-point core values to strings with 2 decimal places.
    
    Test cases:
    - 0.1 should format to '0.10 cores'
    - 1.0 should format to '1.00 cores'
    - 2.5 should format to '2.50 cores'
    """
    assert fmt_cores(0.1) == "0.10 cores"
    assert fmt_cores(1.0) == "1.00 cores"
    assert fmt_cores(2.5) == "2.50 cores"


def test_fmt_bytes_gib():
    """Test formatting bytes to GiB.
    
    This test verifies that the fmt_bytes_gib function correctly converts
    byte values to GiB strings with 2 decimal places.
    
    Test cases:
    - 1 GiB (1073741824 bytes) should format to '1.00 GiB'
    - 2.5 GiB should format to '2.50 GiB'
    - 512 MiB (536870912 bytes) should format to '0.50 GiB'
    """
    # 1 GiB
    assert fmt_bytes_gib(1024 * 1024 * 1024) == "1.00 GiB"
    # 2.5 GiB
    assert fmt_bytes_gib(2.5 * 1024 * 1024 * 1024) == "2.50 GiB"
    # 512 MiB
    assert fmt_bytes_gib(512 * 1024 * 1024) == "0.50 GiB"
