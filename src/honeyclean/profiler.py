"""
Main profiler module for HoneyClean package.
"""

import pandas as pd
import numpy as np
import logging
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from .config import HoneyCleanConfig
from .analyzers.statistical import StatisticalAnalyzer
from .analyzers.type_inference import DataTypeInference
from .analyzers.recommendations import DataCleaningRecommendations
from .analyzers.enhanced import EnhancedAnalyzer
from .visualizations.generators import VisualizationGenerator
from .reports.powerpoint import PowerPointGenerator
from .utils.formatters import StatisticalFormatter

logger = logging.getLogger(__name__)

class AutomatedDataProfiler:
    """Main class for automated data profiling with report generation."""
    
    def __init__(self, config: Optional[HoneyCleanConfig] = None):
        self.config = config or HoneyCleanConfig()
        self.visualization_generator = VisualizationGenerator(self.config)
        self.powerpoint_generator = PowerPointGenerator(self.config)
        
        logger.info("AutomatedDataProfiler initialized")
    
    def profile_dataset(self, data: Union[pd.DataFrame, str, Path], 
                       dataset_name: Optional[str] = None) -> Dict[str, Any]:
        """Profile a complete dataset and generate reports."""
        logger.info("Starting data profiling...")
        
        # Load data if needed
        if isinstance(data, (str, Path)):
            df = pd.read_csv(data)
            dataset_name = dataset_name or Path(data).stem
        else:
            df = data.copy()
            dataset_name = dataset_name or "dataset"
        
        # Generate comprehensive profile
        profiling_results = {
            'dataset_info': self._analyze_dataset_info(df, dataset_name),
            'columns': {},
            'general_recommendations': DataCleaningRecommendations.get_general_recommendations(df)
        }
        
        # Enhanced analysis based on configuration
        if self.config.target_col:
            logger.info("Performing target correlation analysis...")
            profiling_results['target_correlation'] = EnhancedAnalyzer.analyze_target_correlation(df, self.config.target_col)
            profiling_results['target_distribution'] = EnhancedAnalyzer.analyze_target_distribution(df, self.config.target_col)
            
            # Categorical by target analysis for categorical targets
            target_cols = self.config.target_col if isinstance(self.config.target_col, list) else [self.config.target_col]
            for target_col in target_cols:
                if target_col in df.columns and not pd.api.types.is_numeric_dtype(df[target_col]):
                    profiling_results[f'categorical_by_{target_col}'] = EnhancedAnalyzer.analyze_categorical_by_target(df, target_col)
        
        if self.config.id_cols:
            logger.info("Performing ID uniqueness analysis...")
            profiling_results['id_uniqueness'] = EnhancedAnalyzer.check_id_uniqueness(df, self.config.id_cols)
            
            # Check composite ID if multiple ID columns
            if len(self.config.id_cols) > 1:
                profiling_results['composite_id_uniqueness'] = EnhancedAnalyzer.check_composite_id_uniqueness(df, self.config.id_cols)
        
        # Analyze each column
        logger.info("Analyzing individual columns...")
        for column in df.columns:
            logger.debug(f"Analyzing column: {column}")
            column_analysis = self._analyze_column(df[column], column)
            profiling_results['columns'][column] = column_analysis
        
        # Generate reports (no more intermediate visualizations)
        logger.info("Generating reports...")
        report_paths = self._generate_reports(profiling_results, df)
        
        logger.info("Data profiling completed successfully!")
        return {
            'profiling_results': profiling_results,
            'plot_paths': {},  # No intermediate plots
            'report_paths': report_paths
        }
    
    def display_formatted_results(self, profiling_results: Dict[str, Any]) -> str:
        """Display formatted statistical results using enhanced formatting."""
        output = []
        
        # Dataset overview
        dataset_info = profiling_results.get('dataset_info', {})
        output.append("🗂️  DATASET OVERVIEW (数据集概览)")
        output.append("=" * 50)
        output.append(f"Dataset (数据集): {dataset_info.get('name', 'Unknown')}")
        output.append(f"Shape (形状): {dataset_info.get('shape', 'Unknown')}")
        output.append(f"Memory Usage (内存使用): {dataset_info.get('memory_usage_mb', 0):.2f} MB")
        output.append(f"Missing Values (缺失值): {dataset_info.get('total_missing', 0):,} ({dataset_info.get('missing_percentage', 0):.2f}%)")
        output.append(f"Duplicates (重复行): {dataset_info.get('duplicate_count', 0):,}")
        output.append("")
        
        # Target correlation analysis
        if 'target_correlation' in profiling_results:
            for target_col, correlations in profiling_results['target_correlation'].items():
                output.append(StatisticalFormatter.format_correlation_analysis(correlations['correlations'], target_col))
        
        # Target distribution analysis
        if 'target_distribution' in profiling_results:
            for target_col, target_stats in profiling_results['target_distribution'].items():
                output.append(StatisticalFormatter.format_target_distribution(target_stats, target_col))
        
        # ID uniqueness check
        if 'id_uniqueness' in profiling_results:
            output.append(StatisticalFormatter.format_id_uniqueness_check(profiling_results['id_uniqueness']))
        
        # Column-by-column analysis
        output.append("📊 COLUMN ANALYSIS (列分析)")
        output.append("=" * 50)
        
        for column_name, analysis in profiling_results.get('columns', {}).items():
            output.append(f"\n📋 Column (列): {column_name}")
            output.append("-" * 40)
            
            if analysis.get('type') == 'numeric':
                output.append(StatisticalFormatter.format_numeric_stats(analysis))
            elif analysis.get('type') == 'categorical':
                output.append(StatisticalFormatter.format_categorical_stats(analysis))
            elif analysis.get('type') == 'datetime':
                output.append(StatisticalFormatter.format_datetime_stats(analysis))
            else:
                output.append(f"Type (类型): {analysis.get('type', 'Unknown')}")
                output.append(f"Analysis (分析): {analysis}")
            
            # Add recommendations
            recommendations = analysis.get('recommendations', [])
            if recommendations:
                output.append("💡 Recommendations (建议):")
                for rec in recommendations:
                    output.append(f"  • {rec}")
                output.append("")
        
        return "\n".join(output)
    
    def _analyze_dataset_info(self, df: pd.DataFrame, name: str) -> Dict[str, Any]:
        """Analyze general dataset information."""
        memory_usage = df.memory_usage(deep=True).sum() / 1024 / 1024
        missing_count = df.isnull().sum().sum()
        
        return {
            'name': name,
            'shape': df.shape,
            'memory_usage_mb': memory_usage,
            'total_missing': missing_count,
            'missing_percentage': (missing_count / (df.shape[0] * df.shape[1])) * 100,
            'duplicate_count': df.duplicated().sum(),
            'numeric_columns': len(df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': len(df.select_dtypes(include=['object', 'category']).columns),
            'datetime_columns': len(df.select_dtypes(include=['datetime64']).columns),
            'text_columns': len(df.select_dtypes(include=['object']).columns)
        }
    
    def _analyze_column(self, series: pd.Series, column_name: str) -> Dict[str, Any]:
        """Analyze individual column comprehensively."""
        # Infer data type
        type_info = DataTypeInference.infer_column_type(series)
        suggested_type = type_info['suggested_type']
        
        # Perform type-specific analysis
        try:
            if suggested_type == 'numeric' or pd.api.types.is_numeric_dtype(series):
                analysis = StatisticalAnalyzer.analyze_numeric(series)
                analysis['type'] = 'numeric'
                recommendations = DataCleaningRecommendations.get_numeric_recommendations(analysis)
            elif suggested_type in ['categorical', 'text'] or series.dtype == 'object':
                analysis = StatisticalAnalyzer.analyze_categorical(series)
                analysis['type'] = 'categorical'
                recommendations = DataCleaningRecommendations.get_categorical_recommendations(analysis)
            elif suggested_type == 'datetime' or pd.api.types.is_datetime64_any_dtype(series):
                analysis = StatisticalAnalyzer.analyze_datetime(series)
                analysis['type'] = 'datetime'
                recommendations = DataCleaningRecommendations.get_datetime_recommendations(analysis)
            else:
                analysis = StatisticalAnalyzer.analyze_categorical(series)
                analysis['type'] = 'other'
                recommendations = []
        except Exception as e:
            # Fallback analysis if statistical analysis fails
            analysis = {
                'type': 'error',
                'count': len(series),
                'missing_count': series.isnull().sum(),
                'missing_percentage': (series.isnull().sum() / len(series)) * 100,
                'error': str(e)
            }
            recommendations = [f"Analysis failed: {str(e)}"]
        
        # Add type inference information
        analysis['type_inference'] = type_info
        analysis['recommendations'] = recommendations
        
        return analysis
    
    def _generate_reports(self, profiling_results: Dict[str, Any], 
                         df: pd.DataFrame) -> Dict[str, str]:
        """Generate all reports."""
        report_paths = {}
        
        # PowerPoint report - pass original DataFrame
        if self.config.generate_powerpoint:
            ppt_path = self.powerpoint_generator.create_presentation(
                profiling_results, df)
            report_paths['powerpoint'] = ppt_path
        
        # JSON report
        if self.config.generate_json:
            json_path = f"{self.config.output_reports}/profiling_results.json"
            with open(json_path, 'w') as f:
                json.dump(profiling_results, f, indent=2, default=str)
            report_paths['json'] = json_path
        
        # CSV summary
        if self.config.generate_csv_summary:
            csv_path = self._generate_csv_summary(profiling_results)
            report_paths['csv_summary'] = csv_path
        
        return report_paths
    
    def _generate_csv_summary(self, profiling_results: Dict[str, Any]) -> str:
        """Generate CSV summary of profiling results."""
        summary_data = []
        
        for column_name, analysis in profiling_results['columns'].items():
            row = {
                'column_name': column_name,
                'data_type': analysis.get('type', 'unknown'),
                'missing_count': analysis.get('missing_count', 0),
                'missing_percentage': analysis.get('missing_percentage', 0)
            }
            
            if analysis.get('type') == 'numeric':
                row.update({
                    'mean': analysis.get('mean'),
                    'std': analysis.get('std'),
                    'min': analysis.get('min'),
                    'max': analysis.get('max'),
                    'outliers_count': analysis.get('zscore_outliers')
                })
            elif analysis.get('type') == 'categorical':
                row.update({
                    'unique_count': analysis.get('unique_count'),
                    'most_common': analysis.get('mode')
                })
            
            row['recommendations_count'] = len(analysis.get('recommendations', []))
            summary_data.append(row)
        
        summary_df = pd.DataFrame(summary_data)
        csv_path = f"{self.config.output_reports}/column_summary.csv"
        summary_df.to_csv(csv_path, index=False)
        
        return csv_path