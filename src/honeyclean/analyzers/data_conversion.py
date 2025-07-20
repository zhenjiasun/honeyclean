"""
Data type conversion analyzer for automatic float conversion detection.
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)


class DataTypeConverter:
    """Analyzer for detecting and converting data types, especially to float."""
    
    @staticmethod
    def find_and_convert_float_columns(data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Find DataFrame columns that could be converted to float type and convert them.
        
        Parameters:
        data (pandas.DataFrame): The DataFrame to analyze
        
        Returns:
        tuple: (converted_df, conversion_report)
            - converted_df: DataFrame with converted columns
            - conversion_report: Dictionary with details about the conversion
        """
        # Create a copy of the dataframe to avoid modifying the original
        converted_df = data.copy()
        
        # Dictionary to store information about conversion attempts
        conversion_report = {
            "convertible_columns": [],
            "partially_convertible_columns": {},
            "unconvertible_columns": [],
            "already_float_columns": []
        }
        
        # Iterate through each column
        for column in data.columns:
            # Skip columns that are already float type
            if pd.api.types.is_float_dtype(data[column]):
                conversion_report["already_float_columns"].append(column)
                continue
            
            # For each column, attempt to convert to float
            try:
                # Try direct conversion
                converted_df[column] = pd.to_numeric(data[column], errors='raise')
                conversion_report["convertible_columns"].append(column)
            except Exception:
                # Try converting with coerce (sets invalid values to NaN)
                try:
                    converted_series = pd.to_numeric(data[column], errors='coerce')
                    
                    # Check how many values were successfully converted
                    valid_count = converted_series.notna().sum()
                    total_count = len(converted_series)
                    success_rate = valid_count / total_count if total_count > 0 else 0
                    
                    # If more than 90% of values could be converted, consider it partially convertible
                    if success_rate >= 0.9:
                        converted_df[column] = converted_series
                        conversion_report["partially_convertible_columns"][column] = {
                            "success_rate": success_rate,
                            "valid_count": valid_count,
                            "total_count": total_count,
                            "invalid_examples": data[column][converted_series.isna()].head(3).tolist() if any(converted_series.isna()) else []
                        }
                    else:
                        conversion_report["unconvertible_columns"].append(column)
                except Exception:
                    # If even coercion fails, column is not convertible
                    conversion_report["unconvertible_columns"].append(column)
        
        logger.info(f"Found {len(conversion_report['convertible_columns'])} fully convertible columns")
        logger.info(f"Found {len(conversion_report['partially_convertible_columns'])} partially convertible columns")
        logger.info(f"Found {len(conversion_report['unconvertible_columns'])} unconvertible columns")
        logger.info(f"Found {len(conversion_report['already_float_columns'])} columns already in float format")
        
        return converted_df, conversion_report
    
    @staticmethod
    def analyze_conversion_results(conversion_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the conversion results and provide insights.
        
        Parameters:
        conversion_report: Dictionary with conversion results
        
        Returns:
        Dictionary with analysis insights
        """
        total_columns = (len(conversion_report['convertible_columns']) + 
                        len(conversion_report['partially_convertible_columns']) + 
                        len(conversion_report['unconvertible_columns']) + 
                        len(conversion_report['already_float_columns']))
        
        convertible_count = len(conversion_report['convertible_columns'])
        partially_convertible_count = len(conversion_report['partially_convertible_columns'])
        
        analysis = {
            "total_columns": total_columns,
            "conversion_success_rate": (convertible_count + partially_convertible_count) / total_columns if total_columns > 0 else 0,
            "fully_convertible_rate": convertible_count / total_columns if total_columns > 0 else 0,
            "recommendations": []
        }
        
        # Add recommendations based on results
        if convertible_count > 0:
            analysis["recommendations"].append(f"Consider converting {convertible_count} columns to numeric for better analysis")
        
        if partially_convertible_count > 0:
            analysis["recommendations"].append(f"Review {partially_convertible_count} partially convertible columns for data quality issues")
        
        unconvertible_count = len(conversion_report['unconvertible_columns'])
        if unconvertible_count > 0:
            analysis["recommendations"].append(f"Keep {unconvertible_count} categorical columns as text for categorical analysis")
        
        return analysis