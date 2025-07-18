"""
Command Line Interface for HoneyClean package.
"""

import click
import pandas as pd
from pathlib import Path
import sys
import logging
from typing import Optional

from .config import HoneyCleanConfig
from .profiler import AutomatedDataProfiler

logger = logging.getLogger(__name__)

@click.group()
@click.version_option(version="1.0.0")
@click.option('--config', '-c', default='base.toml', 
              help='Path to configuration TOML file')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose logging')
@click.pass_context
def cli(ctx, config: str, verbose: bool):
    """
    HoneyClean - Automated Data Profiling and Cleaning Tool
    
    A comprehensive tool for analyzing datasets, generating cleaning 
    recommendations, and creating professional reports.
    """
    # Setup context
    ctx.ensure_object(dict)
    
    # Load configuration
    try:
        honeyclean_config = HoneyCleanConfig.from_toml(config)
        if verbose:
            honeyclean_config.log_level = "DEBUG"
            honeyclean_config.setup_logging()
        
        ctx.obj['config'] = honeyclean_config
        logger.info(f"HoneyClean v1.0.0 initialized with config: {config}")
        
    except Exception as e:
        click.echo(f"Error loading configuration: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', default=None,
              help='Output directory for reports (overrides config)')
@click.option('--format', '-f', 
              type=click.Choice(['powerpoint', 'json', 'html', 'all']),
              default='all', help='Output format')
@click.option('--sample', '-s', type=int, default=None,
              help='Sample size for large datasets')
@click.pass_context
def profile(ctx, input_file: str, output: Optional[str], 
           format: str, sample: Optional[int]):
    """
    Profile a dataset and generate comprehensive reports.
    
    INPUT_FILE: Path to the CSV file to analyze
    """
    config = ctx.obj['config']
    
    # Override output directory if specified
    if output:
        config.output_reports = output
        config.plots_dir = f"{output}/plots"
        config.create_directories()
    
    # Configure output formats
    if format != 'all':
        config.generate_powerpoint = format == 'powerpoint'
        config.generate_json = format == 'json'
        config.generate_html = format == 'html'
        config.generate_csv_summary = False
    
    try:
        click.echo(f"Loading dataset: {input_file}")
        
        # Load data
        df = pd.read_csv(input_file)
        
        # Sample data if specified
        if sample and len(df) > sample:
            click.echo(f"Sampling {sample} rows from {len(df)} total rows")
            df = df.sample(n=sample, random_state=42)
        
        click.echo(f"Dataset shape: {df.shape}")
        
        # Create profiler and run analysis
        profiler = AutomatedDataProfiler(config)
        
        with click.progressbar(length=100, label='Profiling dataset') as bar:
            results = profiler.profile_dataset(df, Path(input_file).stem)
            bar.update(100)
        
        # Display results summary
        click.echo("\n" + "="*50)
        click.echo("PROFILING COMPLETE")
        click.echo("="*50)
        
        dataset_info = results['profiling_results']['dataset_info']
        click.echo(f"Dataset: {dataset_info['name']}")
        click.echo(f"Shape: {dataset_info['shape'][0]:,} rows × {dataset_info['shape'][1]} columns")
        click.echo(f"Memory Usage: {dataset_info['memory_usage_mb']:.1f} MB")
        click.echo(f"Missing Values: {dataset_info['total_missing']:,} ({dataset_info['missing_percentage']:.1f}%)")
        click.echo(f"Duplicate Rows: {dataset_info['duplicate_count']:,}")
        
        click.echo(f"\nColumn Types:")
        click.echo(f"  • Numeric: {dataset_info['numeric_columns']}")
        click.echo(f"  • Categorical: {dataset_info['categorical_columns']}")
        click.echo(f"  • Datetime: {dataset_info['datetime_columns']}")
        click.echo(f"  • Text: {dataset_info['text_columns']}")
        
        # Show output files
        click.echo(f"\nReports generated in: {config.output_reports}")
        for report_type, report_path in results['report_paths'].items():
            click.echo(f"  • {report_type.upper()}: {report_path}")
        
        click.echo(f"\nVisualizations saved in: {config.plots_dir}")
        
    except Exception as e:
        click.echo(f"Error during profiling: {e}", err=True)
        logger.error(f"Profiling failed: {e}", exc_info=True)
        sys.exit(1)

@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--columns', '-col', multiple=True,
              help='Specific columns to analyze (can be specified multiple times)')
@click.option('--output', '-o', default=None,
              help='Output directory for reports')
@click.pass_context
def analyze(ctx, input_file: str, columns: tuple, output: Optional[str]):
    """
    Analyze specific columns in detail.
    
    INPUT_FILE: Path to the CSV file to analyze
    """
    config = ctx.obj['config']
    
    if output:
        config.output_reports = output
        config.create_directories()
    
    try:
        # Load data
        df = pd.read_csv(input_file)
        
        # Filter columns if specified
        if columns:
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                click.echo(f"Warning: Columns not found: {missing_cols}", err=True)
            
            available_cols = [col for col in columns if col in df.columns]
            if not available_cols:
                click.echo("No valid columns specified", err=True)
                sys.exit(1)
            
            df = df[available_cols]
            click.echo(f"Analyzing columns: {list(available_cols)}")
        
        # Run profiling
        profiler = AutomatedDataProfiler(config)
        results = profiler.profile_dataset(df, f"{Path(input_file).stem}_analysis")
        
        # Display detailed column analysis
        for column_name, analysis in results['profiling_results']['columns'].items():
            click.echo(f"\n{'='*60}")
            click.echo(f"COLUMN: {column_name}")
            click.echo(f"{'='*60}")
            click.echo(f"Type: {analysis['type']}")
            click.echo(f"Missing: {analysis['missing_count']:,} ({analysis['missing_percentage']:.1f}%)")
            
            if analysis['type'] == 'numeric':
                click.echo(f"Mean: {analysis['mean']:.2f}")
                click.echo(f"Std: {analysis['std']:.2f}")
                click.echo(f"Min: {analysis['min']:.2f}")
                click.echo(f"Max: {analysis['max']:.2f}")
                click.echo(f"Outliers: {analysis['zscore_outliers']}")
            elif analysis['type'] == 'categorical':
                click.echo(f"Unique Values: {analysis['unique_count']}")
                click.echo(f"Most Common: {analysis['mode']}")
            
            if analysis['recommendations']:
                click.echo(f"\nRecommendations:")
                for i, rec in enumerate(analysis['recommendations'], 1):
                    click.echo(f"  {i}. {rec}")
        
        click.echo(f"\nDetailed reports saved to: {config.output_reports}")
        
    except Exception as e:
        click.echo(f"Error during analysis: {e}", err=True)
        sys.exit(1)

@cli.command()
@click.option('--config-file', '-c', default='base.toml',
              help='Path to save the configuration file')
@click.option('--force', '-f', is_flag=True,
              help='Overwrite existing configuration file')
def init(config_file: str, force: bool):
    """
    Initialize a new HoneyClean configuration file.
    """
    config_path = Path(config_file)
    
    if config_path.exists() and not force:
        click.echo(f"Configuration file {config_file} already exists. Use --force to overwrite.")
        return
    
    # Create default configuration content
    default_config = '''[honeyclean]
version = "1.0.0"
description = "Automated data profiling and cleaning recommendations"

[paths]
input_data = "./data"
output_reports = "./reports"
temp_dir = "./temp"
plots_dir = "./plots"

[analysis]
chunk_size = 10000
max_memory_mb = 1024
enable_statistical_analysis = true
enable_outlier_detection = true
enable_correlation_analysis = true
enable_distribution_analysis = true

[thresholds]
outlier_threshold = 3.0
correlation_threshold = 0.8
high_cardinality_threshold = 50
missing_value_threshold = 0.05

[visualization]
figure_dpi = 300
figure_width = 12
figure_height = 8
color_palette = "husl"
style = "seaborn-v0_8-whitegrid"

[powerpoint]
slide_width = 13.333
slide_height = 7.5
template_style = "professional"

[output]
generate_html = true
generate_json = true
generate_powerpoint = true
generate_csv_summary = true

[logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
file = "honeyclean.log"
'''
    
    try:
        with open(config_path, 'w') as f:
            f.write(default_config)
        
        click.echo(f"Configuration file created: {config_file}")
        click.echo("You can now customize the settings and run:")
        click.echo(f"  honeyclean profile your_data.csv")
        
    except Exception as e:
        click.echo(f"Error creating configuration file: {e}", err=True)

@cli.command()
@click.pass_context
def info(ctx):
    """
    Display information about the current configuration.
    """
    config = ctx.obj['config']
    
    click.echo("HoneyClean Configuration")
    click.echo("=" * 40)
    
    click.echo(f"Input Data Directory: {config.input_data}")
    click.echo(f"Output Reports Directory: {config.output_reports}")
    click.echo(f"Plots Directory: {config.plots_dir}")
    click.echo(f"Temp Directory: {config.temp_dir}")
    
    click.echo(f"\nAnalysis Settings:")
    click.echo(f"  • Chunk Size: {config.chunk_size:,}")
    click.echo(f"  • Max Memory: {config.max_memory_mb} MB")
    click.echo(f"  • Statistical Analysis: {config.enable_statistical_analysis}")
    click.echo(f"  • Outlier Detection: {config.enable_outlier_detection}")
    click.echo(f"  • Correlation Analysis: {config.enable_correlation_analysis}")
    
    click.echo(f"\nOutput Formats:")
    click.echo(f"  • PowerPoint: {config.generate_powerpoint}")
    click.echo(f"  • JSON: {config.generate_json}")
    click.echo(f"  • HTML: {config.generate_html}")
    click.echo(f"  • CSV Summary: {config.generate_csv_summary}")

if __name__ == '__main__':
    cli()