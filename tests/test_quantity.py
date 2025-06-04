"""Tests for the quantity module."""

import pytest

from kubernetes_dashboard.quantity import (
    cpu_to_cores,
    fmt_bytes_gib,
    fmt_cores,
    mem_to_bytes,
)


def test_cpu_to_cores():
    """Test parsing CPU quantities."""
    assert cpu_to_cores("100m") == 0.1
    assert cpu_to_cores("1") == 1.0
    assert cpu_to_cores("2.5") == 2.5


def test_mem_to_bytes():
    """Test parsing memory quantities."""
    assert mem_to_bytes("1Ki") == 1024
    assert mem_to_bytes("1Mi") == 1024 * 1024
    assert mem_to_bytes("1Gi") == 1024 * 1024 * 1024


def test_fmt_cores():
    """Test formatting CPU cores."""
    assert fmt_cores(0.1) == "0.10 cores"
    assert fmt_cores(1.0) == "1.00 cores"
    assert fmt_cores(2.5) == "2.50 cores"


def test_fmt_bytes_gib():
    """Test formatting bytes to GiB."""
    # 1 GiB
    assert fmt_bytes_gib(1024 * 1024 * 1024) == "1.00 GiB"
    # 2.5 GiB
    assert fmt_bytes_gib(2.5 * 1024 * 1024 * 1024) == "2.50 GiB"
    # 512 MiB
    assert fmt_bytes_gib(512 * 1024 * 1024) == "0.50 GiB"


def test_fmt_percent():
    """Test formatting percentage values."""
    from kubernetes_dashboard.quantity import fmt_percent

    assert fmt_percent(75.5) == "75.50%"
    assert fmt_percent(100.0) == "100.00%"
    assert fmt_percent(0.0) == "0.00%"
    assert fmt_percent("N/A") == "N/A"
