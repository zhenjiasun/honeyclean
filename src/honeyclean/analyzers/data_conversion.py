import pandas as pd
from typing import Tuple, Dict, Any, List
import logging

# Assuming logger is defined elsewhere
logger = logging.getLogger(__name__)

class DataTypeConverter:
    """Analyzer for detecting and converting data types, including float and datetime."""
    
    @staticmethod
    def find_and_convert_columns(data: pd.DataFrame) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Find DataFrame columns that could be converted to float or datetime types and convert them.
        
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
            # Float conversions
            "convertible_float_columns": [],
            "partially_convertible_float_columns": {},
            "unconvertible_float_columns": [],
            "already_float_columns": [],
            
            # DateTime conversions
            "convertible_datetime_columns": [],
            "partially_convertible_datetime_columns": {},
            "unconvertible_datetime_columns": [],
            "already_datetime_columns": [],
            
            # Summary
            "total_columns_processed": 0,
            "conversion_summary": {}
        }
        
        # Process each column
        for column in data.columns:
            conversion_report["total_columns_processed"] += 1
            
            # Check float conversions
            DataTypeConverter._process_float_conversion(
                data, converted_df, column, conversion_report
            )
            
            # Check datetime conversions (only if not already converted to float)
            if column not in conversion_report["convertible_float_columns"]:
                DataTypeConverter._process_datetime_conversion(
                    data, converted_df, column, conversion_report
                )
        
        # Log results
        DataTypeConverter._log_conversion_results(conversion_report)
        
        return converted_df, conversion_report
    
    @staticmethod
    def _process_float_conversion(data: pd.DataFrame, converted_df: pd.DataFrame, 
                                column: str, conversion_report: Dict[str, Any]) -> None:
        """Process float conversion for a single column."""
        
        # Skip columns that are already float type
        if pd.api.types.is_float_dtype(data[column]):
            conversion_report["already_float_columns"].append(column)
            return
        
        # Skip datetime columns
        if pd.api.types.is_datetime64_any_dtype(data[column]):
            return
        
        # Try direct conversion to numeric
        try:
            converted_df[column] = pd.to_numeric(data[column], errors='raise')
            conversion_report["convertible_float_columns"].append(column)
            return
        except (ValueError, TypeError):
            pass
        
        # Try converting with coerce (sets invalid values to NaN)
        try:
            converted_series = pd.to_numeric(data[column], errors='coerce')
            
            # Check how many values were successfully converted
            valid_count = converted_series.notna().sum()
            total_count = len(converted_series)
            success_rate = valid_count / total_count if total_count > 0 else 0
            
            # If more than 90% of values could be converted, consider it partially convertible
            if success_rate >= 0.9 and valid_count > 0:
                converted_df[column] = converted_series
                conversion_report["partially_convertible_float_columns"][column] = {
                    "success_rate": success_rate,
                    "valid_count": valid_count,
                    "total_count": total_count,
                    "invalid_examples": data[column][converted_series.isna()].head(3).tolist() if any(converted_series.isna()) else []
                }
            else:
                conversion_report["unconvertible_float_columns"].append(column)
        except Exception:
            conversion_report["unconvertible_float_columns"].append(column)
    
    @staticmethod
    def _process_datetime_conversion(data: pd.DataFrame, converted_df: pd.DataFrame, 
                                   column: str, conversion_report: Dict[str, Any]) -> None:
        """Process datetime conversion for a single column."""
        
        # Skip columns that are already datetime type
        if pd.api.types.is_datetime64_any_dtype(data[column]):
            conversion_report["already_datetime_columns"].append(column)
            return
        
        # Skip numeric columns (including those we just converted to float)
        if pd.api.types.is_numeric_dtype(converted_df[column]):
            return
        
        # Common datetime formats to try
        datetime_formats = [
            None,  # Let pandas infer
            '%Y-%m-%d',
            '%m/%d/%Y',
            '%d/%m/%Y',
            '%Y-%m-%d %H:%M:%S',
            '%m/%d/%Y %H:%M:%S',
            '%d/%m/%Y %H:%M:%S',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M',
            '%m/%d/%Y %H:%M',
            '%d-%m-%Y',
            '%d-%m-%Y %H:%M:%S'
        ]
        
        # Try direct conversion with different formats
        for fmt in datetime_formats:
            try:
                if fmt is None:
                    # Let pandas infer the format
                    converted_series = pd.to_datetime(data[column], errors='raise', infer_datetime_format=True)
                else:
                    converted_series = pd.to_datetime(data[column], format=fmt, errors='raise')
                
                converted_df[column] = converted_series
                conversion_report["convertible_datetime_columns"].append(column)
                return
            except (ValueError, TypeError):
                continue
        
        # Try converting with coerce for partial conversion
        try:
            converted_series = pd.to_datetime(data[column], errors='coerce', infer_datetime_format=True)
            
            # Check how many values were successfully converted
            valid_count = converted_series.notna().sum()
            total_count = len(converted_series)
            success_rate = valid_count / total_count if total_count > 0 else 0
            
            # If more than 80% of values could be converted, consider it partially convertible
            # (Lower threshold for datetime as they can be more varied)
            if success_rate >= 0.8 and valid_count > 0:
                converted_df[column] = converted_series
                conversion_report["partially_convertible_datetime_columns"][column] = {
                    "success_rate": success_rate,
                    "valid_count": valid_count,
                    "total_count": total_count,
                    "invalid_examples": data[column][converted_series.isna()].head(3).tolist() if any(converted_series.isna()) else []
                }
            else:
                conversion_report["unconvertible_datetime_columns"].append(column)
        except Exception:
            conversion_report["unconvertible_datetime_columns"].append(column)
    
    @staticmethod
    def _log_conversion_results(conversion_report: Dict[str, Any]) -> None:
        """Log the conversion results."""
        logger.info(f"=== Float Conversion Results ===")
        logger.info(f"Fully convertible float columns: {len(conversion_report['convertible_float_columns'])}")
        logger.info(f"Partially convertible float columns: {len(conversion_report['partially_convertible_float_columns'])}")
        logger.info(f"Unconvertible to float: {len(conversion_report['unconvertible_float_columns'])}")
        logger.info(f"Already float columns: {len(conversion_report['already_float_columns'])}")
        
        logger.info(f"=== DateTime Conversion Results ===")
        logger.info(f"Fully convertible datetime columns: {len(conversion_report['convertible_datetime_columns'])}")
        logger.info(f"Partially convertible datetime columns: {len(conversion_report['partially_convertible_datetime_columns'])}")
        logger.info(f"Unconvertible to datetime: {len(conversion_report['unconvertible_datetime_columns'])}")
        logger.info(f"Already datetime columns: {len(conversion_report['already_datetime_columns'])}")
    
    @staticmethod
    def analyze_conversion_results(conversion_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze the conversion results and provide insights.
        
        Parameters:
        conversion_report: Dictionary with conversion results
        
        Returns:
        Dictionary with analysis insights
        """
        total_columns = conversion_report["total_columns_processed"]
        
        # Float conversion statistics
        float_convertible = len(conversion_report['convertible_float_columns'])
        float_partially_convertible = len(conversion_report['partially_convertible_float_columns'])
        float_already_converted = len(conversion_report['already_float_columns'])
        
        # DateTime conversion statistics  
        datetime_convertible = len(conversion_report['convertible_datetime_columns'])
        datetime_partially_convertible = len(conversion_report['partially_convertible_datetime_columns'])
        datetime_already_converted = len(conversion_report['already_datetime_columns'])
        
        analysis = {
            "total_columns": total_columns,
            "float_analysis": {
                "convertible_count": float_convertible,
                "partially_convertible_count": float_partially_convertible,
                "already_float_count": float_already_converted,
                "success_rate": (float_convertible + float_partially_convertible) / total_columns if total_columns > 0 else 0
            },
            "datetime_analysis": {
                "convertible_count": datetime_convertible,
                "partially_convertible_count": datetime_partially_convertible,
                "already_datetime_count": datetime_already_converted,
                "success_rate": (datetime_convertible + datetime_partially_convertible) / total_columns if total_columns > 0 else 0
            },
            "recommendations": []
        }
        
        # Add recommendations based on results
        if float_convertible > 0:
            analysis["recommendations"].append(f"Successfully converted {float_convertible} columns to numeric for better analysis")
        
        if float_partially_convertible > 0:
            analysis["recommendations"].append(f"Review {float_partially_convertible} partially convertible numeric columns for data quality issues")
        
        if datetime_convertible > 0:
            analysis["recommendations"].append(f"Successfully converted {datetime_convertible} columns to datetime for time-series analysis")
        
        if datetime_partially_convertible > 0:
            analysis["recommendations"].append(f"Review {datetime_partially_convertible} partially convertible datetime columns for format inconsistencies")
        
        total_unconvertible = (len(conversion_report['unconvertible_float_columns']) + 
                              len(conversion_report['unconvertible_datetime_columns']))
        if total_unconvertible > 0:
            analysis["recommendations"].append(f"Keep {total_unconvertible} categorical/text columns as-is for categorical analysis")
        
        return analysis
    
    @staticmethod
    def get_conversion_summary(conversion_report: Dict[str, Any]) -> str:
        """
        Get a human-readable summary of the conversion results.
        
        Parameters:
        conversion_report: Dictionary with conversion results
        
        Returns:
        String summary of conversions
        """
        summary_lines = []
        summary_lines.append("=== Data Type Conversion Summary ===")
        
        # Float conversions
        if conversion_report['convertible_float_columns']:
            summary_lines.append(f"✓ Converted to float: {', '.join(conversion_report['convertible_float_columns'])}")
        
        if conversion_report['partially_convertible_float_columns']:
            partial_float = list(conversion_report['partially_convertible_float_columns'].keys())
            summary_lines.append(f"⚠ Partially converted to float: {', '.join(partial_float)}")
        
        # DateTime conversions
        if conversion_report['convertible_datetime_columns']:
            summary_lines.append(f"✓ Converted to datetime: {', '.join(conversion_report['convertible_datetime_columns'])}")
        
        if conversion_report['partially_convertible_datetime_columns']:
            partial_datetime = list(conversion_report['partially_convertible_datetime_columns'].keys())
            summary_lines.append(f"⚠ Partially converted to datetime: {', '.join(partial_datetime)}")
        
        # Already converted
        if conversion_report['already_float_columns']:
            summary_lines.append(f"Already float: {', '.join(conversion_report['already_float_columns'])}")
        
        if conversion_report['already_datetime_columns']:
            summary_lines.append(f"Already datetime: {', '.join(conversion_report['already_datetime_columns'])}")
        
        return '\n'.join(summary_lines)