"""Basic tests for honeyclean package."""

import pytest


def test_import_honeyclean():
    """Test that honeyclean can be imported."""
    import honeyclean

    assert honeyclean is not None


def test_import_config():
    """Test that config module can be imported."""
    from honeyclean.config import HoneyCleanConfig

    assert HoneyCleanConfig is not None


def test_config_defaults():
    """Test that HoneyCleanConfig has sensible defaults."""
    from honeyclean.config import HoneyCleanConfig

    config = HoneyCleanConfig()
    assert config.chunk_size == 10000
    assert config.figure_dpi == 300
    assert config.generate_powerpoint is True


def test_import_profiler():
    """Test that profiler module can be imported."""
    from honeyclean.profiler import AutomatedDataProfiler

    assert AutomatedDataProfiler is not None


def test_import_cli():
    """Test that CLI module can be imported."""
    from honeyclean.cli import cli

    assert cli is not None
