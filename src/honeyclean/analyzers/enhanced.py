"""
Enhanced analyzers for target correlation, ID uniqueness, and target distribution analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List, Union
import logging

logger = logging.getLogger(__name__)


class EnhancedAnalyzer:
    """Enhanced analysis for target correlation and ID uniqueness."""

    @staticmethod
    def analyze_target_correlation(
        df: pd.DataFrame, target_cols: Union[str, List[str]]
    ) -> Dict[str, Any]:
        """Analyze correlation between features and target column(s)."""
        if isinstance(target_cols, str):
            target_cols = [target_cols]

        results = {}

        for target_col in target_cols:
            if target_col not in df.columns:
                logger.warning(f"Target column '{target_col}' not found in dataset")
                continue

            # Get numeric columns only for correlation
            numeric_df = df.select_dtypes(include=[np.number])

            if target_col not in numeric_df.columns:
                logger.warning(
                    f"Target column '{target_col}' is not numeric, skipping correlation analysis"
                )
                continue

            # Calculate correlations
            correlations = numeric_df.corr()[target_col].drop(target_col)

            # Sort by absolute correlation value
            sorted_correlations = correlations.abs().sort_values(ascending=False)

            results[target_col] = {
                "correlations": correlations.to_dict(),
                "sorted_correlations": sorted_correlations.to_dict(),
                "strong_correlations": correlations[
                    correlations.abs() >= 0.7
                ].to_dict(),
                "moderate_correlations": correlations[
                    (correlations.abs() >= 0.3) & (correlations.abs() < 0.7)
                ].to_dict(),
                "weak_correlations": correlations[correlations.abs() < 0.3].to_dict(),
            }

        return results

    @staticmethod
    def analyze_target_distribution(
        df: pd.DataFrame, target_cols: Union[str, List[str]]
    ) -> Dict[str, Any]:
        """Analyze distribution of target column(s)."""
        if isinstance(target_cols, str):
            target_cols = [target_cols]

        results = {}

        for target_col in target_cols:
            if target_col not in df.columns:
                logger.warning(f"Target column '{target_col}' not found in dataset")
                continue

            target_series = df[target_col]

            # Determine if categorical or numeric
            if pd.api.types.is_numeric_dtype(target_series):
                # Numeric target
                from .statistical import StatisticalAnalyzer

                stats = StatisticalAnalyzer.analyze_numeric(target_series)
                stats["type"] = "numeric"
                results[target_col] = stats
            else:
                # Categorical target
                from .statistical import StatisticalAnalyzer

                stats = StatisticalAnalyzer.analyze_categorical(target_series)
                stats["type"] = "categorical"

                # Add class balance analysis
                value_counts = target_series.value_counts()
                total_count = len(target_series)

                # Calculate class balance metrics
                largest_class_pct = (value_counts.iloc[0] / total_count) * 100
                smallest_class_pct = (value_counts.iloc[-1] / total_count) * 100

                stats.update(
                    {
                        "class_balance": {
                            "largest_class_percentage": largest_class_pct,
                            "smallest_class_percentage": smallest_class_pct,
                            "is_balanced": largest_class_pct
                            < 70,  # Threshold for balanced classes
                            "imbalance_ratio": value_counts.iloc[0]
                            / value_counts.iloc[-1],
                        }
                    }
                )

                results[target_col] = stats

        return results

    @staticmethod
    def analyze_categorical_by_target(
        df: pd.DataFrame, target_col: str, categorical_cols: List[str] = None
    ) -> Dict[str, Any]:
        """Analyze categorical column distributions by target column values."""
        if target_col not in df.columns:
            logger.warning(f"Target column '{target_col}' not found in dataset")
            return {}

        if categorical_cols is None:
            categorical_cols = df.select_dtypes(
                include=["object", "category"]
            ).columns.tolist()
            if target_col in categorical_cols:
                categorical_cols.remove(target_col)

        results = {}

        for cat_col in categorical_cols:
            if cat_col not in df.columns:
                continue

            # Create cross-tabulation
            crosstab = pd.crosstab(df[cat_col], df[target_col], normalize="index") * 100

            # Calculate chi-square test if possible
            try:
                from scipy.stats import chi2_contingency

                contingency_table = pd.crosstab(df[cat_col], df[target_col])
                chi2, p_value, dof, expected = chi2_contingency(contingency_table)

                chi_square_results = {
                    "chi_square_statistic": chi2,
                    "p_value": p_value,
                    "degrees_of_freedom": dof,
                    "is_significant": p_value < 0.05,
                }
            except Exception as e:
                chi_square_results = {"error": str(e)}

            results[cat_col] = {
                "crosstab_percentages": crosstab.to_dict(),
                "raw_crosstab": pd.crosstab(df[cat_col], df[target_col]).to_dict(),
                "chi_square_test": chi_square_results,
            }

        return results

    @staticmethod
    def check_id_uniqueness(
        df: pd.DataFrame, id_cols: List[str]
    ) -> Dict[str, Dict[str, Any]]:
        """Check uniqueness of ID columns."""
        results = {}

        for id_col in id_cols:
            if id_col not in df.columns:
                logger.warning(f"ID column '{id_col}' not found in dataset")
                results[id_col] = {"error": f"Column '{id_col}' not found"}
                continue

            series = df[id_col]
            total_count = len(series)
            unique_count = series.nunique()
            duplicate_count = total_count - unique_count
            uniqueness_percentage = (unique_count / total_count) * 100

            # Find duplicate values
            duplicated_mask = series.duplicated(keep=False)
            duplicate_values = series[duplicated_mask].unique()[
                :10
            ]  # Show first 10 duplicates

            # Count occurrences of duplicates
            duplicate_value_counts = (
                series[duplicated_mask].value_counts().head(10).to_dict()
            )

            results[id_col] = {
                "total_count": total_count,
                "unique_count": unique_count,
                "duplicate_count": duplicate_count,
                "uniqueness_percentage": uniqueness_percentage,
                "is_unique": duplicate_count == 0,
                "duplicate_values": (
                    duplicate_values.tolist() if len(duplicate_values) > 0 else []
                ),
                "duplicate_value_counts": duplicate_value_counts,
                "missing_count": series.isnull().sum(),
                "missing_percentage": (series.isnull().sum() / total_count) * 100,
            }

        return results

    @staticmethod
    def check_composite_id_uniqueness(
        df: pd.DataFrame, id_cols: List[str]
    ) -> Dict[str, Any]:
        """Check uniqueness of composite ID (combination of multiple columns)."""
        if not id_cols or len(id_cols) < 2:
            return {"error": "Composite ID requires at least 2 columns"}

        # Check if all columns exist
        missing_cols = [col for col in id_cols if col not in df.columns]
        if missing_cols:
            return {"error": f"Columns not found: {missing_cols}"}

        # Create composite key
        composite_key = df[id_cols].apply(lambda x: "||".join(x.astype(str)), axis=1)

        total_count = len(composite_key)
        unique_count = composite_key.nunique()
        duplicate_count = total_count - unique_count
        uniqueness_percentage = (unique_count / total_count) * 100

        # Find duplicate composite keys
        duplicated_mask = composite_key.duplicated(keep=False)
        duplicate_keys = composite_key[duplicated_mask].unique()[:10]
        duplicate_key_counts = (
            composite_key[duplicated_mask].value_counts().head(10).to_dict()
        )

        return {
            "composite_columns": id_cols,
            "total_count": total_count,
            "unique_count": unique_count,
            "duplicate_count": duplicate_count,
            "uniqueness_percentage": uniqueness_percentage,
            "is_unique": duplicate_count == 0,
            "duplicate_keys": (
                duplicate_keys.tolist() if len(duplicate_keys) > 0 else []
            ),
            "duplicate_key_counts": duplicate_key_counts,
            "missing_count": df[id_cols].isnull().any(axis=1).sum(),
            "missing_percentage": (df[id_cols].isnull().any(axis=1).sum() / total_count)
            * 100,
        }
