"""
Main profiler module for HoneyClean package.
"""

import pandas as pd
import numpy as np
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union

from .config import HoneyCleanConfig
from .analyzers.statistical import StatisticalAnalyzer
from .analyzers.type_inference import DataTypeInference
from .analyzers.recommendations import DataCleaningRecommendations
from .visualizations.generators import VisualizationGenerator
from .reports.powerpoint import PowerPointGenerator

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
        
        # Analyze each column
        logger.info("Analyzing individual columns...")
        for column in df.columns:
            logger.debug(f"Analyzing column: {column}")
            column_analysis = self._analyze_column(df[column], column)
            profiling_results['columns'][column] = column_analysis
        
        # Generate visualizations
        logger.info("Generating visualizations...")
        plot_paths = self._generate_visualizations(df, profiling_results)
        
        # Generate reports
        logger.info("Generating reports...")
        report_paths = self._generate_reports(profiling_results, plot_paths)
        
        logger.info("Data profiling completed successfully!")
        return {
            'profiling_results': profiling_results,
            'plot_paths': plot_paths,
            'report_paths': report_paths
        }
    
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
        
        # Add type inference information
        analysis['type_inference'] = type_info
        analysis['recommendations'] = recommendations
        
        return analysis
    
    def _generate_visualizations(self, df: pd.DataFrame, 
                               profiling_results: Dict[str, Any]) -> Dict[str, str]:
        """Generate all visualizations."""
        plot_paths = {}
        
        # Missing values plot
        missing_plot = self.visualization_generator.create_missing_values_plot(
            df, self.config.plots_dir)
        if missing_plot:
            plot_paths['missing_values'] = missing_plot
        
        # Correlation heatmap
        correlation_plot = self.visualization_generator.create_correlation_heatmap(
            df, self.config.plots_dir)
        if correlation_plot:
            plot_paths['correlation_heatmap'] = correlation_plot
        
        # Individual column plots
        for column_name, column_analysis in profiling_results['columns'].items():
            if column_analysis['type'] == 'numeric':
                plot_path = self.visualization_generator.create_numeric_distribution_plot(
                    df[column_name], column_name, self.config.plots_dir)
                plot_paths[f"{column_name}_distribution"] = plot_path
            elif column_analysis['type'] == 'categorical':
                plot_path = self.visualization_generator.create_categorical_plot(
                    df[column_name], column_name, self.config.plots_dir)
                plot_paths[f"{column_name}_categorical"] = plot_path
        
        return plot_paths
    
    def _generate_reports(self, profiling_results: Dict[str, Any], 
                         plot_paths: Dict[str, str]) -> Dict[str, str]:
        """Generate all reports."""
        report_paths = {}
        
        # PowerPoint report
        if self.config.generate_powerpoint:
            ppt_path = self.powerpoint_generator.create_presentation(
                profiling_results, plot_paths)
            report_paths['powerpoint'] = ppt_path
        
        # JSON report
        if self.config.generate_json:
            import json
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
                'data_type': analysis['type'],
                'missing_count': analysis['missing_count'],
                'missing_percentage': analysis['missing_percentage']
            }
            
            if analysis['type'] == 'numeric':
                row.update({
                    'mean': analysis.get('mean'),
                    'std': analysis.get('std'),
                    'min': analysis.get('min'),
                    'max': analysis.get('max'),
                    'outliers_count': analysis.get('zscore_outliers')
                })
            elif analysis['type'] == 'categorical':
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