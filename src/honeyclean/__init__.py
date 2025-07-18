"""
🍯 HoneyClean - Automated Data Profiling and Cleaning Package
==========================================================

A comprehensive Python package for automated data profiling, cleaning 
recommendations, and professional report generation.

Author: Sunny Sun
Version: 1.0.0
"""

from .profiler import AutomatedDataProfiler
from .config import HoneyCleanConfig
from .analyzers.statistical import StatisticalAnalyzer
from .analyzers.type_inference import DataTypeInference
from .analyzers.recommendations import DataCleaningRecommendations
from .visualizations.generators import VisualizationGenerator
from .reports.powerpoint import PowerPointGenerator

__version__ = "1.0.0"
__author__ = "Sunny Sun"
__email__ = "zhenjiasun@berkeley.edu"

__all__ = [
    'AutomatedDataProfiler',
    'HoneyCleanConfig',
    'StatisticalAnalyzer',
    'DataTypeInference',
    'DataCleaningRecommendations',
    'VisualizationGenerator',
    'PowerPointGenerator'
]