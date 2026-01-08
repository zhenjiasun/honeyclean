"""
Data validation for HoneyClean package.

Provides validation during data loading to detect columns with type inconsistencies.
"""

from typing import Dict, List, Any
import pandas as pd
from pydantic import BaseModel, Field


class ColumnValidationError(BaseModel):
    """Details about validation errors in a specific column."""

    column_name: str = Field(description="Name of the column with validation issues")
    expected_type: str = Field(description="Expected data type for the column")
    error_percentage: float = Field(
        description="Percentage of values that failed validation"
    )
    error_count: int = Field(description="Number of values that failed validation")
    sample_errors: List[Any] = Field(
        default_factory=list, description="Sample of problematic values"
    )


class DataValidationError(Exception):
    """
    Exception raised when data validation fails.

    Contains detailed information about which columns have issues
    and what the problems are.
    """

    def __init__(
        self, message: str, column_errors: List[ColumnValidationError]
    ) -> None:
        self.message = message
        self.column_errors = column_errors
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Format a detailed error message."""
        lines = [self.message, "", "Column validation errors:"]
        for error in self.column_errors:
            lines.append(f"  • {error.column_name}:")
            lines.append(f"      Expected type: {error.expected_type}")
            lines.append(
                f"      Error rate: {error.error_percentage:.2%} ({error.error_count} values)"
            )
            if error.sample_errors:
                samples = ", ".join(repr(v) for v in error.sample_errors[:5])
                lines.append(f"      Sample errors: {samples}")
        return "\n".join(lines)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "message": self.message,
            "column_errors": [e.model_dump() for e in self.column_errors],
        }


class DataValidator:
    """
    Validates DataFrame columns for type consistency.

    Detects columns that should be numeric but contain string values
    below a configurable threshold.
    """

    def __init__(self, threshold: float = 0.05) -> None:
        """
        Initialize the validator.

        Args:
            threshold: Maximum percentage of non-numeric values allowed
                      in a numeric column (default 5%)
        """
        if not 0 <= threshold <= 1:
            raise ValueError("threshold must be between 0 and 1")
        self.threshold = threshold

    def validate_dataframe(self, df: pd.DataFrame) -> None:
        """
        Validate a DataFrame for type consistency.

        Raises:
            DataValidationError: If any columns have type inconsistencies
        """
        errors = self._detect_messy_numeric_columns(df)

        if errors:
            raise DataValidationError(
                message=f"Data validation failed: {len(errors)} column(s) have type inconsistencies",
                column_errors=errors,
            )

    def _detect_messy_numeric_columns(
        self, df: pd.DataFrame
    ) -> List[ColumnValidationError]:
        """
        Detect columns that are mostly numeric but have some string values.

        A column is considered "messy" if:
        - It has object dtype (strings)
        - More than (1 - threshold) of values can be converted to numeric
        - Less than threshold of values are non-numeric strings
        """
        errors = []

        for col in df.columns:
            # Only check object (string) columns
            if df[col].dtype != "object":
                continue

            # Skip columns that are mostly empty
            non_null = df[col].dropna()
            if len(non_null) == 0:
                continue

            # Try to convert to numeric
            numeric_converted = pd.to_numeric(non_null, errors="coerce")
            failed_conversion = numeric_converted.isna() & non_null.notna()

            # Count failures
            failure_count = failed_conversion.sum()
            failure_rate = failure_count / len(non_null)

            # Check if this is a messy numeric column:
            # - Has some numeric values (more than threshold are numeric)
            # - Has some but not too many string values (less than threshold)
            numeric_rate = 1 - failure_rate

            if numeric_rate >= (1 - self.threshold) and failure_count > 0:
                # This column should be numeric but has string contamination
                problematic_values = non_null[failed_conversion].unique().tolist()

                errors.append(
                    ColumnValidationError(
                        column_name=col,
                        expected_type="numeric (int/float)",
                        error_percentage=failure_rate,
                        error_count=int(failure_count),
                        sample_errors=problematic_values[:10],  # Limit to 10 samples
                    )
                )

        return errors
