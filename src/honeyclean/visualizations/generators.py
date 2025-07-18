"""
Generate professional visualizations for different data types.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from scipy import stats
from pathlib import Path
import warnings
from typing import Optional

from ..config import HoneyCleanConfig

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class VisualizationGenerator:
    """Generate professional visualizations for different data types."""
    
    def __init__(self, config: HoneyCleanConfig):
        self.config = config
        self._setup_matplotlib()
    
    def _setup_matplotlib(self):
        """Setup matplotlib with professional styling."""
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams.update({
            'figure.dpi': self.config.figure_dpi,
            'savefig.dpi': self.config.figure_dpi,
            'figure.figsize': (self.config.figure_width, self.config.figure_height),
            'font.size': 12,
            'axes.titlesize': 16,
            'axes.labelsize': 14,
            'lines.linewidth': 2.5,
            'axes.facecolor': 'white',
            'figure.facecolor': 'white'
        })
        sns.set_palette(self.config.color_palette)
    
    def create_numeric_distribution_plot(self, series: pd.Series, column_name: str, 
                                       output_path: str) -> str:
        """Create comprehensive distribution plot for numeric data."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Distribution Analysis: {column_name}', fontsize=16, fontweight='bold')
        
        clean_series = series.dropna()
        
        # Histogram with KDE
        sns.histplot(clean_series, kde=True, ax=axes[0, 0])
        axes[0, 0].set_title('Histogram with KDE')
        axes[0, 0].set_xlabel(column_name)
        
        # Box plot
        sns.boxplot(y=clean_series, ax=axes[0, 1])
        axes[0, 1].set_title('Box Plot')
        axes[0, 1].set_ylabel(column_name)
        
        # Q-Q plot
        stats.probplot(clean_series, dist="norm", plot=axes[1, 0])
        axes[1, 0].set_title('Q-Q Plot (Normal)')
        
        # Violin plot
        sns.violinplot(y=clean_series, ax=axes[1, 1])
        axes[1, 1].set_title('Violin Plot')
        axes[1, 1].set_ylabel(column_name)
        
        plt.tight_layout()
        
        # Save plot
        plot_path = f"{output_path}/{column_name}_distribution.png"
        plt.savefig(plot_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return plot_path
    
    def create_categorical_plot(self, series: pd.Series, column_name: str, 
                               output_path: str) -> str:
        """Create comprehensive categorical analysis plot."""
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle(f'Categorical Analysis: {column_name}', fontsize=16, fontweight='bold')
        
        # Count plot
        top_categories = series.value_counts().head(10)
        sns.barplot(x=top_categories.values, y=top_categories.index, ax=axes[0, 0])
        axes[0, 0].set_title('Top 10 Categories')
        axes[0, 0].set_xlabel('Count')
        
        # Pie chart for top categories
        if len(top_categories) <= 8:
            axes[0, 1].pie(top_categories.values, labels=top_categories.index, autopct='%1.1f%%')
            axes[0, 1].set_title('Category Distribution')
        else:
            # Bar chart for percentages
            percentages = (top_categories / len(series) * 100)
            sns.barplot(x=percentages.values, y=percentages.index, ax=axes[0, 1])
            axes[0, 1].set_title('Top 10 Categories (%)')
            axes[0, 1].set_xlabel('Percentage')
        
        # Frequency distribution
        freq_counts = series.value_counts().value_counts().sort_index()
        sns.barplot(x=freq_counts.index, y=freq_counts.values, ax=axes[1, 0])
        axes[1, 0].set_title('Frequency Distribution')
        axes[1, 0].set_xlabel('Frequency')
        axes[1, 0].set_ylabel('Number of Categories')
        
        # Cumulative frequency
        cumulative = (series.value_counts().sort_values(ascending=False).cumsum() / len(series) * 100)
        axes[1, 1].plot(range(len(cumulative)), cumulative.values)
        axes[1, 1].set_title('Cumulative Frequency')
        axes[1, 1].set_xlabel('Category Rank')
        axes[1, 1].set_ylabel('Cumulative Percentage')
        axes[1, 1].axhline(y=80, color='red', linestyle='--', label='80% Line')
        axes[1, 1].legend()
        
        plt.tight_layout()
        
        # Save plot
        plot_path = f"{output_path}/{column_name}_categorical.png"
        plt.savefig(plot_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return plot_path
    
    def create_correlation_heatmap(self, df: pd.DataFrame, output_path: str) -> Optional[str]:
        """Create correlation heatmap for numerical columns."""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        if len(numeric_cols) < 2:
            return None
        
        plt.figure(figsize=(12, 10))
        corr_matrix = df[numeric_cols].corr()
        
        # Create heatmap
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0, 
                   square=True, linewidths=0.5, cbar_kws={"shrink": .8})
        plt.title('Correlation Heatmap', fontsize=16, fontweight='bold')
        plt.tight_layout()
        
        # Save plot
        plot_path = f"{output_path}/correlation_heatmap.png"
        plt.savefig(plot_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return plot_path
    
    def create_missing_values_plot(self, df: pd.DataFrame, output_path: str) -> str:
        """Create missing values visualization."""
        fig, axes = plt.subplots(1, 2, figsize=(15, 6))
        
        # Missing values heatmap
        missing_data = df.isnull()
        sns.heatmap(missing_data, cbar=True, cmap='viridis', ax=axes[0])
        axes[0].set_title('Missing Values Heatmap')
        axes[0].set_xlabel('Columns')
        axes[0].set_ylabel('Rows')
        
        # Missing values bar chart
        missing_counts = df.isnull().sum()
        missing_counts = missing_counts[missing_counts > 0].sort_values(ascending=False)
        
        if len(missing_counts) > 0:
            missing_counts.plot(kind='bar', ax=axes[1])
            axes[1].set_title('Missing Values by Column')
            axes[1].set_xlabel('Columns')
            axes[1].set_ylabel('Missing Count')
            axes[1].tick_params(axis='x', rotation=45)
        else:
            axes[1].text(0.5, 0.5, 'No Missing Values', ha='center', va='center', 
                        transform=axes[1].transAxes, fontsize=14)
            axes[1].set_title('Missing Values by Column')
        
        plt.tight_layout()
        
        # Save plot
        plot_path = f"{output_path}/missing_values.png"
        plt.savefig(plot_path, dpi=self.config.figure_dpi, bbox_inches='tight')
        plt.close()
        
        return plot_path