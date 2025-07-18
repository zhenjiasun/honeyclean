"""
Configuration management for HoneyClean package.
"""

import sys
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass
import logging

# Handle tomllib import for Python < 3.11
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        import tomllib

logger = logging.getLogger(__name__)

@dataclass
class HoneyCleanConfig:
    """Configuration class for HoneyClean profiler."""
    
    # Paths
    input_data: str = "./data"
    output_reports: str = "./reports"
    temp_dir: str = "./temp"
    plots_dir: str = "./plots"
    
    # Analysis settings
    chunk_size: int = 10000
    max_memory_mb: int = 1024
    enable_statistical_analysis: bool = True
    enable_outlier_detection: bool = True
    enable_correlation_analysis: bool = True
    enable_distribution_analysis: bool = True
    
    # Thresholds
    outlier_threshold: float = 3.0
    correlation_threshold: float = 0.8
    high_cardinality_threshold: int = 50
    missing_value_threshold: float = 0.05
    
    # Visualization settings
    figure_dpi: int = 300
    figure_width: int = 12
    figure_height: int = 8
    color_palette: str = "husl"
    style: str = "seaborn-v0_8-whitegrid"
    
    # PowerPoint settings
    slide_width: float = 13.333
    slide_height: float = 7.5
    template_style: str = "professional"
    
    # Output formats
    generate_html: bool = True
    generate_json: bool = True
    generate_powerpoint: bool = True
    generate_csv_summary: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    log_file: str = "honeyclean.log"
    
    def __post_init__(self):
        """Create directories and setup logging after initialization."""
        self.create_directories()
        self.setup_logging()
    
    def create_directories(self):
        """Create necessary directories."""
        directories = [self.output_reports, self.temp_dir, self.plots_dir]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    def setup_logging(self):
        """Setup logging configuration."""
        log_level = getattr(logging, self.log_level.upper())
        logging.basicConfig(
            level=log_level,
            format=self.log_format,
            handlers=[
                logging.FileHandler(self.log_file),
                logging.StreamHandler()
            ]
        )
    
    @classmethod
    def from_toml(cls, config_path: str = "base.toml") -> 'HoneyCleanConfig':
        """Load configuration from TOML file."""
        config_file = Path(config_path)
        
        if not config_file.exists():
            logger.warning(f"Config file {config_path} not found. Using defaults.")
            return cls()
        
        try:
            with open(config_file, 'rb') as f:
                toml_data = tomllib.load(f)
            
            # Extract configuration sections
            paths = toml_data.get('paths', {})
            analysis = toml_data.get('analysis', {})
            thresholds = toml_data.get('thresholds', {})
            visualization = toml_data.get('visualization', {})
            powerpoint = toml_data.get('powerpoint', {})
            output = toml_data.get('output', {})
            logging_config = toml_data.get('logging', {})
            
            # Create config instance
            config = cls(
                # Paths
                input_data=paths.get('input_data', './data'),
                output_reports=paths.get('output_reports', './reports'),
                temp_dir=paths.get('temp_dir', './temp'),
                plots_dir=paths.get('plots_dir', './plots'),
                
                # Analysis
                chunk_size=analysis.get('chunk_size', 10000),
                max_memory_mb=analysis.get('max_memory_mb', 1024),
                enable_statistical_analysis=analysis.get('enable_statistical_analysis', True),
                enable_outlier_detection=analysis.get('enable_outlier_detection', True),
                enable_correlation_analysis=analysis.get('enable_correlation_analysis', True),
                enable_distribution_analysis=analysis.get('enable_distribution_analysis', True),
                
                # Thresholds
                outlier_threshold=thresholds.get('outlier_threshold', 3.0),
                correlation_threshold=thresholds.get('correlation_threshold', 0.8),
                high_cardinality_threshold=thresholds.get('high_cardinality_threshold', 50),
                missing_value_threshold=thresholds.get('missing_value_threshold', 0.05),
                
                # Visualization
                figure_dpi=visualization.get('figure_dpi', 300),
                figure_width=visualization.get('figure_width', 12),
                figure_height=visualization.get('figure_height', 8),
                color_palette=visualization.get('color_palette', 'husl'),
                style=visualization.get('style', 'seaborn-v0_8-whitegrid'),
                
                # PowerPoint
                slide_width=powerpoint.get('slide_width', 13.333),
                slide_height=powerpoint.get('slide_height', 7.5),
                template_style=powerpoint.get('template_style', 'professional'),
                
                # Output
                generate_html=output.get('generate_html', True),
                generate_json=output.get('generate_json', True),
                generate_powerpoint=output.get('generate_powerpoint', True),
                generate_csv_summary=output.get('generate_csv_summary', True),
                
                # Logging
                log_level=logging_config.get('level', 'INFO'),
                log_format=logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
                log_file=logging_config.get('file', 'honeyclean.log')
            )
            
            logger.info(f"Configuration loaded from {config_path}")
            return config
            
        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return cls()