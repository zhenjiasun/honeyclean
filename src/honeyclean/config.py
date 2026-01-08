"""
Configuration management for HoneyClean package.
"""

import sys
from pathlib import Path
from typing import Optional, List, Union
import logging

from pydantic import BaseModel, Field, field_validator, model_validator

# Handle tomllib import for Python < 3.11
if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomli as tomllib
    except ImportError:
        import tomllib

logger = logging.getLogger(__name__)


class HoneyCleanConfig(BaseModel):
    """Configuration class for HoneyClean profiler with Pydantic validation."""

    # Paths
    input_data: str = Field(
        default="./data", description="Path to input data file or directory"
    )
    output_reports: str = Field(
        default="./reports", description="Path to output reports directory"
    )

    # Analysis settings
    chunk_size: int = Field(
        default=10000, gt=0, description="Chunk size for processing large datasets"
    )
    max_memory_mb: int = Field(
        default=1024, gt=0, description="Maximum memory usage in MB"
    )
    enable_statistical_analysis: bool = Field(
        default=True, description="Enable statistical analysis"
    )
    enable_outlier_detection: bool = Field(
        default=True, description="Enable outlier detection"
    )
    enable_correlation_analysis: bool = Field(
        default=True, description="Enable correlation analysis"
    )
    enable_distribution_analysis: bool = Field(
        default=True, description="Enable distribution analysis"
    )

    # Thresholds
    outlier_threshold: float = Field(
        default=3.0, gt=0, description="Z-score threshold for outlier detection"
    )
    correlation_threshold: float = Field(
        default=0.8, ge=0, le=1, description="Correlation threshold (0-1)"
    )
    high_cardinality_threshold: int = Field(
        default=50, gt=0, description="Threshold for high cardinality columns"
    )
    missing_value_threshold: float = Field(
        default=0.05, ge=0, le=1, description="Missing value threshold (0-1)"
    )

    # Visualization settings
    figure_dpi: int = Field(
        default=300, gt=0, description="Figure DPI for visualizations"
    )
    figure_width: int = Field(default=12, gt=0, description="Figure width in inches")
    figure_height: int = Field(default=8, gt=0, description="Figure height in inches")
    color_palette: str = Field(default="husl", description="Seaborn color palette")
    style: str = Field(default="seaborn-v0_8-whitegrid", description="Matplotlib style")

    # PowerPoint settings
    slide_width: float = Field(
        default=13.333, gt=0, description="Slide width in inches"
    )
    slide_height: float = Field(default=7.5, gt=0, description="Slide height in inches")
    template_style: str = Field(
        default="professional", description="PowerPoint template style"
    )
    top_correlations_display: int = Field(
        default=20, gt=0, description="Number of top/bottom correlations to display"
    )

    # Output formats
    generate_html: bool = Field(default=True, description="Generate HTML report")
    generate_json: bool = Field(default=True, description="Generate JSON report")
    generate_powerpoint: bool = Field(
        default=True, description="Generate PowerPoint report"
    )
    generate_csv_summary: bool = Field(default=True, description="Generate CSV summary")

    # Target and ID columns configuration
    target_col: Optional[Union[str, List[str]]] = Field(
        default=None, description="Target column(s) for analysis"
    )
    id_cols: Optional[List[str]] = Field(
        default=None, description="ID column(s) for uniqueness checking"
    )

    # Logging
    log_level: str = Field(default="INFO", description="Logging level")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        description="Log format string",
    )
    log_file: str = Field(default="honeyclean.log", description="Log file path")

    model_config = {"extra": "ignore"}

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is a valid Python logging level."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        upper_v = v.upper()
        if upper_v not in valid_levels:
            raise ValueError(f"log_level must be one of {valid_levels}, got '{v}'")
        return upper_v

    @model_validator(mode="after")
    def setup_after_validation(self) -> "HoneyCleanConfig":
        """Setup logging after validation."""
        self.setup_logging()
        return self

    def create_directories(self) -> None:
        """Create necessary directories."""
        directories = [self.output_reports]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)

    def setup_logging(self) -> None:
        """Setup logging configuration."""
        log_level = getattr(logging, self.log_level.upper())
        logging.basicConfig(
            level=log_level,
            format=self.log_format,
            handlers=[logging.FileHandler(self.log_file), logging.StreamHandler()],
        )

    @classmethod
    def from_toml(cls, config_path: str = "base.toml") -> "HoneyCleanConfig":
        """Load configuration from TOML file."""
        config_file = Path(config_path)

        if not config_file.exists():
            logger.warning(f"Config file {config_path} not found. Using defaults.")
            return cls()

        try:
            with open(config_file, "rb") as f:
                toml_data = tomllib.load(f)

            # Extract configuration sections
            paths = toml_data.get("paths", {})
            analysis = toml_data.get("analysis", {})
            thresholds = toml_data.get("thresholds", {})
            visualization = toml_data.get("visualization", {})
            powerpoint = toml_data.get("powerpoint", {})
            output = toml_data.get("output", {})
            logging_config = toml_data.get("logging", {})
            columns = toml_data.get("columns", {})

            # Build config dict - Pydantic will validate all values
            config_dict = {
                # Paths
                "input_data": paths.get("input_data", "./data"),
                "output_reports": paths.get("output_reports", "./reports"),
                # Analysis
                "chunk_size": analysis.get("chunk_size", 10000),
                "max_memory_mb": analysis.get("max_memory_mb", 1024),
                "enable_statistical_analysis": analysis.get(
                    "enable_statistical_analysis", True
                ),
                "enable_outlier_detection": analysis.get(
                    "enable_outlier_detection", True
                ),
                "enable_correlation_analysis": analysis.get(
                    "enable_correlation_analysis", True
                ),
                "enable_distribution_analysis": analysis.get(
                    "enable_distribution_analysis", True
                ),
                # Thresholds
                "outlier_threshold": thresholds.get("outlier_threshold", 3.0),
                "correlation_threshold": thresholds.get("correlation_threshold", 0.8),
                "high_cardinality_threshold": thresholds.get(
                    "high_cardinality_threshold", 50
                ),
                "missing_value_threshold": thresholds.get(
                    "missing_value_threshold", 0.05
                ),
                # Visualization
                "figure_dpi": visualization.get("figure_dpi", 300),
                "figure_width": visualization.get("figure_width", 12),
                "figure_height": visualization.get("figure_height", 8),
                "color_palette": visualization.get("color_palette", "husl"),
                "style": visualization.get("style", "seaborn-v0_8-whitegrid"),
                # PowerPoint
                "slide_width": powerpoint.get("slide_width", 13.333),
                "slide_height": powerpoint.get("slide_height", 7.5),
                "template_style": powerpoint.get("template_style", "professional"),
                "top_correlations_display": powerpoint.get(
                    "top_correlations_display", 20
                ),
                # Output
                "generate_html": output.get("generate_html", True),
                "generate_json": output.get("generate_json", True),
                "generate_powerpoint": output.get("generate_powerpoint", True),
                "generate_csv_summary": output.get("generate_csv_summary", True),
                # Target and ID columns
                "target_col": columns.get("target_col"),
                "id_cols": columns.get("id_cols"),
                # Logging
                "log_level": logging_config.get("level", "INFO"),
                "log_format": logging_config.get(
                    "format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
                ),
                "log_file": logging_config.get("file", "honeyclean.log"),
            }

            config = cls(**config_dict)
            logger.info(f"Configuration loaded from {config_path}")
            return config

        except Exception as e:
            logger.error(f"Error loading configuration: {e}")
            return cls()
