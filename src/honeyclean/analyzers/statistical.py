"""
Comprehensive statistical analysis for different data types.
"""

import pandas as pd
import numpy as np
from scipy import stats
from typing import Dict, Any, List


class StatisticalAnalyzer:
    """Comprehensive statistical analysis for different data types."""

    @staticmethod
    def analyze_numeric(series: pd.Series) -> Dict[str, Any]:
        """Analyze numerical column comprehensively."""
        clean_series = series.dropna()

        if len(clean_series) == 0:
            return {"error": "No valid numeric values found"}

        # Basic statistics
        stats_dict = {
            "count": len(clean_series),
            "missing_count": series.isnull().sum(),
            "missing_percentage": (series.isnull().sum() / len(series)) * 100,
            "mean": clean_series.mean(),
            "median": clean_series.median(),
            "mode": (
                clean_series.mode().iloc[0] if not clean_series.mode().empty else None
            ),
            "std": clean_series.std(),
            "var": clean_series.var(),
            "min": clean_series.min(),
            "max": clean_series.max(),
            "range": clean_series.max() - clean_series.min(),
            "q1": clean_series.quantile(0.25),
            "q3": clean_series.quantile(0.75),
            "iqr": clean_series.quantile(0.75) - clean_series.quantile(0.25),
            "skewness": clean_series.skew(),
            "kurtosis": clean_series.kurtosis(),
            "coefficient_of_variation": (
                clean_series.std() / clean_series.mean()
                if clean_series.mean() != 0
                else np.nan
            ),
        }

        # Outlier detection
        stats_dict.update(StatisticalAnalyzer._detect_outliers(clean_series))

        # Distribution analysis
        stats_dict.update(StatisticalAnalyzer._analyze_distribution(clean_series))

        return stats_dict

    @staticmethod
    def analyze_categorical(series: pd.Series) -> Dict[str, Any]:
        """Analyze categorical column comprehensively."""
        return {
            "count": len(series),
            "missing_count": series.isnull().sum(),
            "missing_percentage": (series.isnull().sum() / len(series)) * 100,
            "unique_count": series.nunique(),
            "cardinality": series.nunique() / len(series),
            "mode": series.mode().iloc[0] if not series.mode().empty else None,
            "value_counts": series.value_counts().head(10).to_dict(),
            "value_percentages": (
                series.value_counts().head(10) / len(series) * 100
            ).to_dict(),
            "rare_categories": StatisticalAnalyzer._identify_rare_categories(series),
            "is_high_cardinality": series.nunique() > 50,
        }

    @staticmethod
    def analyze_datetime(series: pd.Series) -> Dict[str, Any]:
        """Analyze datetime column comprehensively."""
        try:
            dt_series = pd.to_datetime(series, errors="coerce")
            clean_series = dt_series.dropna()

            if len(clean_series) == 0:
                return {"error": "No valid datetime values found"}

            return {
                "count": len(clean_series),
                "missing_count": dt_series.isnull().sum(),
                "missing_percentage": (dt_series.isnull().sum() / len(dt_series)) * 100,
                "min_date": clean_series.min(),
                "max_date": clean_series.max(),
                "date_range": clean_series.max() - clean_series.min(),
                "year_range": clean_series.dt.year.max() - clean_series.dt.year.min(),
                "unique_years": clean_series.dt.year.nunique(),
                "unique_months": clean_series.dt.month.nunique(),
                "unique_days": clean_series.dt.day.nunique(),
                "weekday_distribution": clean_series.dt.day_name()
                .value_counts()
                .to_dict(),
                "month_distribution": clean_series.dt.month_name()
                .value_counts()
                .to_dict(),
            }
        except Exception as e:
            return {"error": f"Datetime analysis failed: {str(e)}"}

    @staticmethod
    def _detect_outliers(series: pd.Series) -> Dict[str, Any]:
        """Detect outliers using multiple methods."""
        outlier_info = {}

        # Z-score method
        z_scores = np.abs(stats.zscore(series))
        zscore_outliers = series[z_scores > 3]
        outlier_info["zscore_outliers"] = len(zscore_outliers)
        outlier_info["zscore_percentage"] = (len(zscore_outliers) / len(series)) * 100

        # IQR method
        Q1 = series.quantile(0.25)
        Q3 = series.quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        iqr_outliers = series[(series < lower_bound) | (series > upper_bound)]
        outlier_info["iqr_outliers"] = len(iqr_outliers)
        outlier_info["iqr_percentage"] = (len(iqr_outliers) / len(series)) * 100
        outlier_info["iqr_lower_bound"] = lower_bound
        outlier_info["iqr_upper_bound"] = upper_bound

        # Modified Z-score method
        median = series.median()
        mad = np.median(np.abs(series - median))
        modified_z_scores = (
            0.6745 * (series - median) / mad if mad != 0 else np.zeros_like(series)
        )
        modified_zscore_outliers = series[np.abs(modified_z_scores) > 3.5]
        outlier_info["modified_zscore_outliers"] = len(modified_zscore_outliers)
        outlier_info["modified_zscore_percentage"] = (
            len(modified_zscore_outliers) / len(series)
        ) * 100

        return outlier_info

    @staticmethod
    def _analyze_distribution(series: pd.Series) -> Dict[str, Any]:
        """Analyze distribution characteristics."""
        distribution_info = {}

        # Normality tests
        try:
            if len(series) > 3:
                shapiro_stat, shapiro_p = stats.shapiro(series)
                distribution_info["shapiro_statistic"] = shapiro_stat
                distribution_info["shapiro_p_value"] = shapiro_p
                distribution_info["is_normal"] = shapiro_p > 0.05

            if len(series) > 8:
                dagostino_stat, dagostino_p = stats.normaltest(series)
                distribution_info["dagostino_statistic"] = dagostino_stat
                distribution_info["dagostino_p_value"] = dagostino_p
        except Exception as e:
            distribution_info["normality_test_error"] = str(e)

        # Distribution characteristics
        distribution_info["is_skewed"] = abs(series.skew()) > 1
        distribution_info["is_heavy_tailed"] = series.kurtosis() > 3

        return distribution_info

    @staticmethod
    def _identify_rare_categories(
        series: pd.Series, threshold: float = 0.01
    ) -> List[str]:
        """Identify rare categories below threshold."""
        value_counts = series.value_counts(normalize=True)
        rare_categories = value_counts[value_counts < threshold].index.tolist()
        return rare_categories
