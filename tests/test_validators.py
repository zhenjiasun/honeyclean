"""Tests for data validation in HoneyClean."""

import pytest
import pandas as pd

from honeyclean.validators import (
    DataValidator,
    DataValidationError,
    ColumnValidationError,
)


class TestDataValidator:
    """Tests for DataValidator class."""

    def test_clean_numeric_column_passes(self):
        """Test that clean numeric columns pass validation."""
        df = pd.DataFrame({"amount": [100, 200, 300, 400, 500]})
        validator = DataValidator(threshold=0.05)
        validator.validate_dataframe(df)  # Should not raise

    def test_clean_string_column_passes(self):
        """Test that string columns are not flagged."""
        df = pd.DataFrame({"name": ["Alice", "Bob", "Charlie", "Diana", "Eve"]})
        validator = DataValidator(threshold=0.05)
        validator.validate_dataframe(df)  # Should not raise

    def test_messy_numeric_column_raises_error(self):
        """Test that messy numeric columns raise DataValidationError."""
        # 96 numeric values, 4 string values = 4% error rate
        values = [str(i) for i in range(96)] + ["N/A", "unknown", "-", "null"]
        df = pd.DataFrame({"amount": values})

        validator = DataValidator(threshold=0.05)
        with pytest.raises(DataValidationError) as exc_info:
            validator.validate_dataframe(df)

        error = exc_info.value
        assert len(error.column_errors) == 1
        assert error.column_errors[0].column_name == "amount"
        assert "N/A" in error.column_errors[0].sample_errors

    def test_threshold_respected(self):
        """Test that threshold is respected.
        
        The validator flags columns where numeric_rate >= (1 - threshold).
        With 10% errors (90% numeric), threshold must be > 10% to NOT flag it.
        """
        # 90 numeric values, 10 string values = 10% error rate (90% numeric)
        values = [str(i) for i in range(90)] + ["error"] * 10
        df = pd.DataFrame({"amount": values})

        # 5% threshold: 90% >= 95%? No, so should NOT flag
        validator = DataValidator(threshold=0.05)
        validator.validate_dataframe(df)  # Should not raise

        # 20% threshold: 90% >= 80%? Yes, so should flag
        validator = DataValidator(threshold=0.20)
        with pytest.raises(DataValidationError):
            validator.validate_dataframe(df)

    def test_mostly_string_column_passes(self):
        """Test that columns with >50% strings are not flagged as messy numeric."""
        values = ["alice", "bob", "charlie", "diana", "eve"] + ["1", "2"]
        df = pd.DataFrame({"name": values})

        validator = DataValidator(threshold=0.05)
        validator.validate_dataframe(df)  # Should not raise

    def test_multiple_messy_columns(self):
        """Test detection of multiple messy columns."""
        df = pd.DataFrame(
            {
                "amount": [str(i) for i in range(98)] + ["N/A", "error"],
                "price": [str(i) for i in range(99)] + ["unknown"],
            }
        )

        validator = DataValidator(threshold=0.05)
        with pytest.raises(DataValidationError) as exc_info:
            validator.validate_dataframe(df)

        error = exc_info.value
        assert len(error.column_errors) == 2
        column_names = [e.column_name for e in error.column_errors]
        assert "amount" in column_names
        assert "price" in column_names

    def test_error_message_formatting(self):
        """Test that error messages are properly formatted."""
        values = [str(i) for i in range(98)] + ["N/A", "error"]
        df = pd.DataFrame({"amount": values})

        validator = DataValidator(threshold=0.05)
        with pytest.raises(DataValidationError) as exc_info:
            validator.validate_dataframe(df)

        error_str = str(exc_info.value)
        assert "amount" in error_str
        assert "numeric" in error_str

    def test_to_dict(self):
        """Test error serialization to dict."""
        values = [str(i) for i in range(98)] + ["N/A", "error"]
        df = pd.DataFrame({"amount": values})

        validator = DataValidator(threshold=0.05)
        with pytest.raises(DataValidationError) as exc_info:
            validator.validate_dataframe(df)

        error_dict = exc_info.value.to_dict()
        assert "message" in error_dict
        assert "column_errors" in error_dict
        assert len(error_dict["column_errors"]) == 1

    def test_invalid_threshold_raises_error(self):
        """Test that invalid threshold raises ValueError."""
        with pytest.raises(ValueError):
            DataValidator(threshold=-0.1)

        with pytest.raises(ValueError):
            DataValidator(threshold=1.5)

    def test_empty_dataframe_passes(self):
        """Test that empty DataFrames pass validation."""
        df = pd.DataFrame()
        validator = DataValidator(threshold=0.05)
        validator.validate_dataframe(df)  # Should not raise

    def test_null_values_handled(self):
        """Test that null values are handled correctly."""
        values = [str(i) for i in range(95)] + [None, None, "N/A", "error", None]
        df = pd.DataFrame({"amount": values})

        validator = DataValidator(threshold=0.05)
        with pytest.raises(DataValidationError) as exc_info:
            validator.validate_dataframe(df)

        # Only non-null string values should be counted as errors
        error = exc_info.value
        assert error.column_errors[0].error_count == 2  # N/A and error


class TestColumnValidationError:
    """Tests for ColumnValidationError model."""

    def test_create_error(self):
        """Test creating a ColumnValidationError."""
        error = ColumnValidationError(
            column_name="amount",
            expected_type="numeric",
            error_percentage=0.05,
            error_count=5,
            sample_errors=["N/A", "unknown"],
        )
        assert error.column_name == "amount"
        assert error.expected_type == "numeric"
        assert error.error_percentage == 0.05
        assert error.error_count == 5
        assert error.sample_errors == ["N/A", "unknown"]
