"""
Generate professional PowerPoint presentations from profiling results.
"""

from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from datetime import datetime
from pathlib import Path
from typing import Dict, Any
import io

from ..config import HoneyCleanConfig
from ..visualizations.generators import VisualizationGenerator

class PowerPointGenerator:
    """Generate professional PowerPoint presentations from profiling results."""
    
    def __init__(self, config: HoneyCleanConfig):
        self.config = config
        self.viz_generator = VisualizationGenerator(config)
    
    def create_presentation(self, profiling_results: Dict[str, Any], 
                          df_original) -> str:
        """Create comprehensive PowerPoint presentation with embedded plots."""
        prs = Presentation()
        
        # Set slide dimensions
        prs.slide_width = Inches(self.config.slide_width)
        prs.slide_height = Inches(self.config.slide_height)
        
        # Create slides
        self._create_title_slide(prs, profiling_results)
        self._create_overview_slide(prs, profiling_results)
        self._create_missing_values_slide(prs, df_original)
        
        # Create individual column slides
        for column_name, column_analysis in profiling_results['columns'].items():
            self._create_column_slide(prs, column_name, column_analysis, df_original[column_name])
        
        self._create_recommendations_slide(prs, profiling_results)
        
        # Save presentation
        output_path = f"{self.config.output_reports}/data_profiling_report.pptx"
        prs.save(output_path)
        
        return output_path
    
    def _create_title_slide(self, prs: Presentation, results: Dict[str, Any]):
        """Create title slide."""
        slide_layout = prs.slide_layouts[0]
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        subtitle = slide.placeholders[1]
        
        title.text = "数据分析报告"
        subtitle.text = f"数据集: {results['dataset_info']['name']}\n生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        title.text_frame.paragraphs[0].font.size = Pt(44)
        title.text_frame.paragraphs[0].font.bold = True
        title.text_frame.paragraphs[0].font.color.rgb = RGBColor(0, 51, 102)
    
    def _create_overview_slide(self, prs: Presentation, results: Dict[str, Any]):
        """Create dataset overview slide."""
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        content = slide.placeholders[1]
        
        title.text = "数据集概览"
        
        info = results['dataset_info']
        overview_text = f"""数据集摘要:
- 数据规模: {info['shape'][0]:,} 行 × {info['shape'][1]} 列
- 内存使用: {info['memory_usage_mb']:.1f} MB
- 缺失值: {info['total_missing']:,} ({info['missing_percentage']:.1f}%)
- 重复行: {info['duplicate_count']:,}

列类型分布:
- 数值型: {info['numeric_columns']} 列
- 分类型: {info['categorical_columns']} 列
- 日期型: {info['datetime_columns']} 列
- 文本型: {info['text_columns']} 列"""
        
        content.text = overview_text
    
    def _create_missing_values_slide(self, prs: Presentation, df):
        """Create missing values analysis slide."""
        slide_layout = prs.slide_layouts[6]  # Blank
        slide = prs.slides.add_slide(slide_layout)
        
        # Add title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.5), Inches(12), Inches(1))
        title_frame = title_box.text_frame
        title_frame.text = "缺失值分析"
        title_frame.paragraphs[0].font.size = Pt(32)
        title_frame.paragraphs[0].font.bold = True
        
        # Generate and add plot
        try:
            plot_buffer = self.viz_generator.create_missing_values_summary(df)
            if plot_buffer:
                slide.shapes.add_picture(plot_buffer, Inches(1), Inches(1.5), Inches(11), Inches(5))
        except Exception as e:
            # Add error message if plot fails
            error_box = slide.shapes.add_textbox(Inches(1), Inches(3), Inches(11), Inches(2))
            error_frame = error_box.text_frame
            error_frame.text = f"图表生成失败: {str(e)}"
    
    def _create_column_slide(self, prs: Presentation, column_name: str, 
                           analysis: Dict[str, Any], series):
        """Create individual column analysis slide."""
        slide_layout = prs.slide_layouts[6]  # Blank
        slide = prs.slides.add_slide(slide_layout)
        
        # Add title
        title_box = slide.shapes.add_textbox(Inches(0.5), Inches(0.3), Inches(12), Inches(0.8))
        title_frame = title_box.text_frame
        title_frame.text = f"特征分析: {column_name}"
        title_frame.paragraphs[0].font.size = Pt(24)
        title_frame.paragraphs[0].font.bold = True
        
        # Handle different analysis types
        if analysis.get('type') == 'numeric' and 'error' not in analysis:
            try:
                # Create numeric plots
                hist_buffer, percentile_buffer = self.viz_generator.create_numeric_plot_for_ppt(series, column_name)
                
                if hist_buffer:
                    slide.shapes.add_picture(hist_buffer, Inches(0.5), Inches(1.2), Inches(6), Inches(3))
                
                if percentile_buffer:
                    slide.shapes.add_picture(percentile_buffer, Inches(6.8), Inches(1.2), Inches(6), Inches(3))
                
                # Add statistics text
                stats_box = slide.shapes.add_textbox(Inches(0.5), Inches(4.5), Inches(12), Inches(2.5))
                stats_frame = stats_box.text_frame
                stats_frame.word_wrap = True
                
                stats_text = f"""统计信息:
- 总数: {analysis.get('count', 0):,} | 缺失: {analysis.get('missing_count', 0):,} ({analysis.get('missing_percentage', 0):.1f}%)
- 均值: {analysis.get('mean', 0):.2f} | 标准差: {analysis.get('std', 0):.2f}
- 最小值: {analysis.get('min', 0):.2f} | 最大值: {analysis.get('max', 0):.2f}
- 异常值 (Z-score): {analysis.get('zscore_outliers', 0)} | 偏度: {analysis.get('skewness', 0):.2f}"""
                
                stats_frame.text = stats_text
                
            except Exception as e:
                # Add error message if plots fail
                error_box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11), Inches(3))
                error_frame = error_box.text_frame
                error_frame.text = f"数值型变量图表生成失败: {str(e)}"
                
        elif analysis.get('type') == 'categorical' and 'error' not in analysis:
            try:
                # Create categorical plot
                plot_buffer = self.viz_generator.create_categorical_plot_for_ppt(series, column_name)
                
                if plot_buffer:
                    slide.shapes.add_picture(plot_buffer, Inches(0.5), Inches(1.2), Inches(12), Inches(4))
                
                # Add statistics text
                stats_box = slide.shapes.add_textbox(Inches(0.5), Inches(5.5), Inches(12), Inches(1.5))
                stats_frame = stats_box.text_frame
                stats_frame.word_wrap = True
                
                stats_text = f"""统计信息:
- 总数: {analysis.get('count', 0):,} | 缺失: {analysis.get('missing_count', 0):,} ({analysis.get('missing_percentage', 0):.1f}%)
- 唯一值: {analysis.get('unique_count', 0)} | 基数比: {analysis.get('cardinality', 0):.3f}
- 最频繁值: {analysis.get('mode', 'N/A')} | 高基数: {'是' if analysis.get('is_high_cardinality', False) else '否'}"""
                
                stats_frame.text = stats_text
                
            except Exception as e:
                # Add error message if plots fail
                error_box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11), Inches(3))
                error_frame = error_box.text_frame
                error_frame.text = f"分类型变量图表生成失败: {str(e)}"
        else:
            # Error case or unsupported type
            error_box = slide.shapes.add_textbox(Inches(1), Inches(2), Inches(11), Inches(4))
            error_frame = error_box.text_frame
            error_text = f"""变量类型: {analysis.get('type', 'unknown')}
总数: {analysis.get('count', 0):,}
缺失值: {analysis.get('missing_count', 0):,} ({analysis.get('missing_percentage', 0):.1f}%)

{analysis.get('error', '该变量类型暂不支持详细分析')}"""
            error_frame.text = error_text
        
        # Add recommendations
        if analysis.get('recommendations'):
            rec_box = slide.shapes.add_textbox(Inches(0.5), Inches(6.5), Inches(12), Inches(1))
            rec_frame = rec_box.text_frame
            rec_frame.word_wrap = True
            
            recommendations_text = "清洗建议:\n" + "\n".join([f"• {rec}" for rec in analysis['recommendations'][:3]])  # Show top 3
            rec_frame.text = recommendations_text
            rec_frame.paragraphs[0].font.bold = True
    
    def _create_recommendations_slide(self, prs: Presentation, results: Dict[str, Any]):
        """Create general recommendations slide."""
        slide_layout = prs.slide_layouts[1]
        slide = prs.slides.add_slide(slide_layout)
        
        title = slide.shapes.title
        content = slide.placeholders[1]
        
        title.text = "数据清洗建议"
        
        all_recommendations = results.get('general_recommendations', [])
        
        if all_recommendations:
            recommendations_text = "整体数据集建议:\n\n" + "\n".join([f"• {rec}" for rec in all_recommendations])
            content.text = recommendations_text
        else:
            content.text = "数据集状况良好，无特殊建议。"