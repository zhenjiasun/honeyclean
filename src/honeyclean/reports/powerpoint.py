"""
Generate professional PowerPoint presentations from profiling results.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

from ..config import HoneyCleanConfig

class PowerPointGenerator:
    """Generate professional PowerPoint presentations from profiling results."""
    
    def __init__(self, config: HoneyCleanConfig):
        self.config = config
    
    def create_presentation(self, profiling_results: Dict[str, Any], 
                          plot_paths: Dict[str, str]) -> str:
        """Create comprehensive PowerPoint presentation."""
        prs = Presentation()
        
        # Set slide dimensions
        prs.slide_width = Inches(self.config.slide_width)
        prs.slide_height = Inches(self.config.slide_height)
        
        # Create slides
        self._create_title_slide(prs, profiling_results)
        self._create_overview_slide(prs, profiling_results)
        self._create_missing_values_slide(prs, profiling_results, plot_paths)
        self._create_correlation_slide(prs, profiling_results, plot_paths)
        
        # Create individual column slides
        for column_name, column_analysis in profiling_results['columns'].items():
            self._create_column_slide(prs, column_name, column_analysis, plot_paths)
        
        self._create_recommendations_slide(prs, profiling_results)
        
        # Save presentation
        output_path = f"{self.config.output_reports}/data_profiling_report.pptx"
        prs.save(output_path)
        
        return output_path
    
    def _create_title_slide(self, prs: Presentation, results: Dict[str, Any]):
        """Create title slide."""
        slide_layout = prs.slide_layouts[0]  # Title slide
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        
        title.text = "Data Profiling Report"
        subtitle.text = f"Dataset: {results['dataset_info']['name']}\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        # Format title
        title.text_frame.paragraphs[0].font.size = Pt(44)
        title.text_frame.paragraphs[0].font.bold = True
        title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)
    
    def _create_overview_slide(self, prs: Presentation, results: Dict[str, Any]):
        """Create dataset overview slide."""
        slide_layout = prs.slide_layouts[1]  # Title and Content
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        content = slide.placeholders[1]
        
        title.text = "Dataset Overview"
        
        # Create overview content
        info = results['dataset_info']
        overview_text = f"""Dataset Summary:
- Shape: {info['shape'][0]:,} rows × {info['shape'][1]} columns
- Memory Usage: {info['memory_usage_mb']:.1f} MB
- Missing Values: {info['total_missing']:,} ({info['missing_percentage']:.1f}%)
- Duplicate Rows: {info['duplicate_count']:,}

Column Types:
- Numeric: {info['numeric_columns']} columns
- Categorical: {info['categorical_columns']} columns
- Datetime: {info['datetime_columns']} columns
- Text: {info['text_columns']} columns"""
        
        content.text = overview_text
    
    def _create_missing_values_slide(self, prs: Presentation, results: Dict[str, Any], 
                                   plot_paths: Dict[str, str]):
        """Create missing values analysis slide."""
        slide_layout = prs.slide_layouts[6]  # Blank
        slide = prs.slides.add_slide(slide_layout)
        
        # Add title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(1))
        title_frame = title_box.text_frame
        title_frame.text = "Missing Values Analysis"
        title_frame.paragraphs[0].font.size = Pt(32)
        title_frame.paragraphs[0].font.bold = True
        
        # Add plot if available
        if 'missing_values' in plot_paths and Path(plot_paths['missing_values']).exists():
            slide.shapes.add_picture(plot_paths['missing_values'], 
                                   Inches(0.5), Inches(1.5), Inches(12), Inches(5))
    
    def _create_correlation_slide(self, prs: Presentation, results: Dict[str, Any], 
                                plot_paths: Dict[str, str]):
        """Create correlation analysis slide."""
        slide_layout = prs.slide_layouts[6]  # Blank
        slide = prs.slides.add_slide(slide_layout)
        
        # Add title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(1))
        title_frame = title_box.text_frame
        title_frame.text = "Correlation Analysis"
        title_frame.paragraphs[0].font.size = Pt(32)
        title_frame.paragraphs[0].font.bold = True
        
        # Add plot if available
        if 'correlation_heatmap' in plot_paths and Path(plot_paths['correlation_heatmap']).exists():
            slide.shapes.add_picture(plot_paths['correlation_heatmap'], 
                                   Inches(0.5), Inches(1.5), Inches(12), Inches(5))
    
    def _create_column_slide(self, prs: Presentation, column_name: str, 
                           analysis: Dict[str, Any], plot_paths: Dict[str, str]):
        """Create individual column analysis slide."""
        slide_layout = prs.slide_layouts[6]  # Blank
        slide = prs.slides.add_slide(slide_layout)
        
        # Add title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(1))
        title_frame = title_box.text_frame
        title_frame.text = f"Column Analysis: {column_name}"
        title_frame.paragraphs[0].font.size = Pt(28)
        title_frame.paragraphs[0].font.bold = True
        
        # Add plot
        plot_key = f"{column_name}_distribution" if analysis['type'] == 'numeric' else f"{column_name}_categorical"
        if plot_key in plot_paths and Path(plot_paths[plot_key]).exists():
            slide.shapes.add_picture(plot_paths[plot_key], 
                                   Inches(0.5), Inches(1.5), Inches(8), Inches(5))
        
        # Add statistics and recommendations
        stats_box = slide.shapes.add_textbox(Inches(8.5), Inches(1.5), Inches(4.5), Inches(5))
        stats_frame = stats_box.text_frame
        stats_frame.word_wrap = True
        
        # Format statistics text
        stats_text = self._format_column_stats(analysis)
        stats_frame.text = stats_text
        
        # Add recommendations
        recommendations_text = "\n".join([f"• {rec}" for rec in analysis.get('recommendations', [])])
        if recommendations_text:
            stats_frame.text += f"\n\nRecommendations:\n{recommendations_text}"
    
    def _create_recommendations_slide(self, prs: Presentation, results: Dict[str, Any]):
        """Create general recommendations slide."""
        slide_layout = prs.slide_layouts[1]  # Title and Content
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        content = slide.placeholders[1]
        
        title.text = "Data Cleaning Recommendations"
        
        # Compile all recommendations
        all_recommendations = results.get('general_recommendations', [])
        
        if all_recommendations:
            recommendations_text = "\n".join([f"• {rec}" for rec in all_recommendations])
            content.text = f"General Dataset Recommendations:\n\n{recommendations_text}"
        else:
            content.text = "No specific recommendations. Dataset appears to be in good condition."
    
    def _format_column_stats(self, analysis: Dict[str, Any]) -> str:
        """Format column statistics for display."""
        stats_text = f"Type: {analysis['type']}\n"
        
        if analysis['type'] == 'numeric':
            stats_text += f"""
Count: {analysis['count']:,}
Missing: {analysis['missing_count']:,} ({analysis['missing_percentage']:.1f}%)
Mean: {analysis['mean']:.2f}
Std: {analysis['std']:.2f}
Min: {analysis['min']:.2f}
Max: {analysis['max']:.2f}
Outliers: {analysis['zscore_outliers']}
Skewness: {analysis['skewness']:.2f}"""
        
        elif analysis['type'] == 'categorical':
            stats_text += f"""
Count: {analysis['count']:,}
Missing: {analysis['missing_count']:,} ({analysis['missing_percentage']:.1f}%)
Unique: {analysis['unique_count']}
Cardinality: {analysis['cardinality']:.3f}
Mode: {analysis['mode']}"""
        
        return stats_text