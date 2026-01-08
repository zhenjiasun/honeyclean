"""Tests for Pydantic validation in HoneyCleanConfig."""

import pytest
from pydantic import ValidationError

from honeyclean.config import HoneyCleanConfig


class TestHoneyCleanConfigValidation:
    """Test input validation for HoneyCleanConfig."""

    def test_valid_default_config(self):
        """Test that default config is valid."""
        config = HoneyCleanConfig()
        assert config.chunk_size == 10000
        assert config.correlation_threshold == 0.8
        assert config.log_level == "INFO"

    def test_chunk_size_must_be_positive(self):
        """Test that chunk_size must be > 0."""
        with pytest.raises(ValidationError) as exc_info:
            HoneyCleanConfig(chunk_size=0)
        assert "chunk_size" in str(exc_info.value)

    def test_chunk_size_negative_invalid(self):
        """Test that negative chunk_size is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            HoneyCleanConfig(chunk_size=-100)
        assert "chunk_size" in str(exc_info.value)

    def test_max_memory_must_be_positive(self):
        """Test that max_memory_mb must be > 0."""
        with pytest.raises(ValidationError) as exc_info:
            HoneyCleanConfig(max_memory_mb=0)
        assert "max_memory_mb" in str(exc_info.value)

    def test_correlation_threshold_range(self):
        """Test that correlation_threshold must be between 0 and 1."""
        # Valid values
        config = HoneyCleanConfig(correlation_threshold=0.5)
        assert config.correlation_threshold == 0.5

        config = HoneyCleanConfig(correlation_threshold=0.0)
        assert config.correlation_threshold == 0.0

        config = HoneyCleanConfig(correlation_threshold=1.0)
        assert config.correlation_threshold == 1.0

    def test_correlation_threshold_above_one_invalid(self):
        """Test that correlation_threshold > 1 is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            HoneyCleanConfig(correlation_threshold=1.5)
        assert "correlation_threshold" in str(exc_info.value)

    def test_correlation_threshold_negative_invalid(self):
        """Test that negative correlation_threshold is invalid."""
        with pytest.raises(ValidationError) as exc_info:
            HoneyCleanConfig(correlation_threshold=-0.1)
        assert "correlation_threshold" in str(exc_info.value)

    def test_missing_value_threshold_range(self):
        """Test that missing_value_threshold must be between 0 and 1."""
        config = HoneyCleanConfig(missing_value_threshold=0.5)
        assert config.missing_value_threshold == 0.5

        with pytest.raises(ValidationError):
            HoneyCleanConfig(missing_value_threshold=1.5)

    def test_log_level_validation(self):
        """Test that log_level must be valid."""
        # Valid levels
        for level in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            config = HoneyCleanConfig(log_level=level)
            assert config.log_level == level

        # Case insensitive
        config = HoneyCleanConfig(log_level="info")
        assert config.log_level == "INFO"

    def test_log_level_invalid(self):
        """Test that invalid log_level raises error."""
        with pytest.raises(ValidationError) as exc_info:
            HoneyCleanConfig(log_level="INVALID")
        assert "log_level" in str(exc_info.value)

    def test_figure_dpi_must_be_positive(self):
        """Test that figure_dpi must be > 0."""
        with pytest.raises(ValidationError) as exc_info:
            HoneyCleanConfig(figure_dpi=0)
        assert "figure_dpi" in str(exc_info.value)

    def test_top_correlations_display_must_be_positive(self):
        """Test that top_correlations_display must be > 0."""
        with pytest.raises(ValidationError) as exc_info:
            HoneyCleanConfig(top_correlations_display=0)
        assert "top_correlations_display" in str(exc_info.value)

    def test_slide_dimensions_must_be_positive(self):
        """Test that slide dimensions must be > 0."""
        with pytest.raises(ValidationError):
            HoneyCleanConfig(slide_width=0)

        with pytest.raises(ValidationError):
            HoneyCleanConfig(slide_height=-1)

    def test_custom_valid_config(self):
        """Test creating a valid custom config."""
        config = HoneyCleanConfig(
            chunk_size=5000,
            max_memory_mb=2048,
            correlation_threshold=0.9,
            missing_value_threshold=0.1,
            log_level="DEBUG",
            figure_dpi=150,
        )
        assert config.chunk_size == 5000
        assert config.max_memory_mb == 2048
        assert config.correlation_threshold == 0.9
        assert config.missing_value_threshold == 0.1
        assert config.log_level == "DEBUG"
        assert config.figure_dpi == 150

    def test_extra_fields_ignored(self):
        """Test that extra fields are ignored."""
        config = HoneyCleanConfig(unknown_field="value")
        assert not hasattr(config, "unknown_field")
