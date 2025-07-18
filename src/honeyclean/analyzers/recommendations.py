"""
Generate intelligent data cleaning recommendations.
"""

import pandas as pd
from typing import Dict, Any, List

class DataCleaningRecommendations:
    """Generate intelligent data cleaning recommendations."""
    
    @staticmethod
    def get_numeric_recommendations(analysis: Dict[str, Any]) -> List[str]:
        """Get cleaning recommendations for numeric columns."""
        recommendations = []
        
        # Check if analysis has error
        if 'error' in analysis:
            recommendations.append(f"Analysis error: {analysis['error']}")
            return recommendations
        
        # Missing values - use .get() with default value
        missing_pct = analysis.get('missing_percentage', 0)
        if missing_pct > 5:
            recommendations.append(f"High missing values ({missing_pct:.1f}%). Consider imputation with median or advanced methods.")
        
        # Outliers
        zscore_outliers = analysis.get('zscore_outliers', 0)
        if zscore_outliers > 0:
            recommendations.append(f"Found {zscore_outliers} outliers using Z-score method. Consider investigation or removal.")
        
        iqr_outliers = analysis.get('iqr_outliers', 0)
        if iqr_outliers > 0:
            recommendations.append(f"Found {iqr_outliers} outliers using IQR method. Consider winsorization or transformation.")
        
        # Skewness
        skewness = analysis.get('skewness', 0)
        if abs(skewness) > 2:
            recommendations.append(f"High skewness ({skewness:.2f}). Consider log transformation or Box-Cox transformation.")
        
        # Distribution
        if not analysis.get('is_normal', True):
            recommendations.append("Data is not normally distributed. Consider transformation for parametric tests.")
        
        # High coefficient of variation
        cv = analysis.get('coefficient_of_variation', 0)
        if cv > 1:
            recommendations.append(f"High variability (CV = {cv:.2f}). Consider normalization or standardization.")
        
        return recommendations
    
    @staticmethod
    def get_categorical_recommendations(analysis: Dict[str, Any]) -> List[str]:
        """Get cleaning recommendations for categorical columns."""
        recommendations = []
        
        # Check if analysis has error
        if 'error' in analysis:
            recommendations.append(f"Analysis error: {analysis['error']}")
            return recommendations
        
        # Missing values
        missing_pct = analysis.get('missing_percentage', 0)
        if missing_pct > 5:
            recommendations.append(f"High missing values ({missing_pct:.1f}%). Consider creating 'Unknown' category or mode imputation.")
        
        # High cardinality
        if analysis.get('is_high_cardinality', False):
            unique_count = analysis.get('unique_count', 0)
            recommendations.append(f"High cardinality ({unique_count} unique values). Consider grouping rare categories or target encoding.")
        
        # Rare categories
        rare_categories = analysis.get('rare_categories', [])
        if rare_categories:
            recommendations.append(f"Found {len(rare_categories)} rare categories. Consider grouping into 'Other' category.")
        
        # Imbalanced categories
        value_counts = analysis.get('value_counts', {})
        if value_counts and len(value_counts) > 1:
            max_count = max(value_counts.values())
            min_count = min(value_counts.values())
            if max_count / min_count > 10:
                recommendations.append("Highly imbalanced categories. Consider resampling or weighting for modeling.")
        
        return recommendations
    
    @staticmethod
    def get_datetime_recommendations(analysis: Dict[str, Any]) -> List[str]:
        """Get cleaning recommendations for datetime columns."""
        recommendations = []
        
        # Check if analysis has error
        if 'error' in analysis:
            recommendations.append(f"Analysis error: {analysis['error']}")
            return recommendations
        
        # Missing values
        missing_pct = analysis.get('missing_percentage', 0)
        if missing_pct > 5:
            recommendations.append(f"High missing values ({missing_pct:.1f}%). Consider forward-fill or interpolation.")
        
        # Date range
        year_range = analysis.get('year_range', 0)
        if year_range > 50:
            recommendations.append("Wide date range. Verify if all dates are valid and consider filtering outliers.")
        
        # Feature extraction
        recommendations.append("Consider extracting features: year, month, day, weekday, season, quarter.")
        
        return recommendations
    
    @staticmethod
    def get_general_recommendations(df: pd.DataFrame) -> List[str]:
        """Get general dataset recommendations."""
        recommendations = []
        
        try:
            # Dataset size
            if len(df) < 100:
                recommendations.append("Small dataset. Consider collecting more data for robust analysis.")
            elif len(df) > 1000000:
                recommendations.append("Large dataset. Consider sampling or chunking for memory efficiency.")
            
            # Memory usage
            memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
            if memory_mb > 1000:
                recommendations.append(f"High memory usage ({memory_mb:.1f} MB). Consider optimizing data types or processing in chunks.")
            
            # Duplicate rows
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                recommendations.append(f"Found {duplicate_count} duplicate rows. Consider removing duplicates.")
                
        except Exception as e:
            recommendations.append(f"Error in general analysis: {str(e)}")
        
        return recommendations