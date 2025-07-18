"""
Generate professional visualizations for different data types.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import platform
import io
import base64
from typing import Optional, Tuple

from ..config import HoneyCleanConfig

# Suppress warnings for cleaner output
warnings.filterwarnings('ignore')

class VisualizationGenerator:
    """Generate professional visualizations for different data types."""
    
    def __init__(self, config: HoneyCleanConfig):
        self.config = config
        self._setup_chinese_fonts()
        self._setup_matplotlib()
    
    def _setup_chinese_fonts(self):
        """Setup Chinese font support for matplotlib."""
        try:
            # 设置中文字体 - 使用用户验证过的设置
            plt.rcParams['font.family'] = 'Heiti TC'
            plt.rcParams['axes.unicode_minus'] = False
            
            # 测试字体是否工作
            fig, ax = plt.subplots(figsize=(1, 1))
            ax.text(0.5, 0.5, '测试中文字体', fontsize=12)
            plt.close(fig)
            print("Chinese font set to: Heiti TC")
            
        except Exception as e:
            print(f"Warning: Could not set up Chinese fonts: {e}")
            # 备用字体设置
            try:
                plt.rcParams['font.family'] = ['SimHei', 'DejaVu Sans']
                plt.rcParams['axes.unicode_minus'] = False
            except:
                pass
    
    def _setup_matplotlib(self):
        """Setup matplotlib with professional styling."""
        plt.style.use('seaborn-v0_8-whitegrid')
        plt.rcParams.update({
            'font.family': 'Heiti TC',  # 确保字体设置
            'axes.unicode_minus': False,  # 修复负号显示
            'figure.dpi': 150,
            'savefig.dpi': 150,
            'font.size': 12,
            'axes.titlesize': 16,
            'axes.labelsize': 14,
            'lines.linewidth': 2,
            'axes.facecolor': 'white',
            'figure.facecolor': 'white',
        })
        sns.set_palette(self.config.color_palette)
    
    def _ensure_chinese_font(self):
        """确保每次绘图前都设置好中文字体"""
        plt.rcParams['font.family'] = 'Heiti TC'
        plt.rcParams['axes.unicode_minus'] = False
    
    def create_numeric_plot_for_ppt(self, series: pd.Series, column_name: str) -> Tuple[io.BytesIO, io.BytesIO]:
        """Create histogram and percentiles chart for numerical data - returns in-memory images."""
        clean_series = series.dropna()
        
        if len(clean_series) == 0:
            return None, None
        
        # 确保中文字体设置
        self._ensure_chinese_font()
        
        # Create histogram with mean/median
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        
        try:
            # Histogram
            n, bins, patches = ax1.hist(clean_series, bins=30, alpha=0.7, color='steelblue', edgecolor='black')
            
            # Add mean and median lines
            mean_val = clean_series.mean()
            median_val = clean_series.median()
            
            ax1.axvline(mean_val, color='red', linestyle='--', linewidth=3, label=f'均值: {mean_val:.2f}')
            ax1.axvline(median_val, color='orange', linestyle='-', linewidth=3, label=f'中位数: {median_val:.2f}')
            
            # 设置标题和轴标签
            ax1.set_title(f'{column_name} - 分布直方图', fontsize=16, fontweight='bold')
            ax1.set_xlabel(f'{column_name} 数值', fontsize=14)
            ax1.set_ylabel('频数', fontsize=14)
            ax1.legend(fontsize=12)
            ax1.grid(True, alpha=0.3)
            
            # 美化刻度标签
            ax1.tick_params(axis='both', which='major', labelsize=12)
            
            plt.tight_layout()
            
            # Save to memory
            hist_buffer = io.BytesIO()
            plt.savefig(hist_buffer, format='png', bbox_inches='tight', dpi=150, 
                       facecolor='white', edgecolor='none')
            hist_buffer.seek(0)
            plt.close()
            
        except Exception as e:
            plt.close()
            print(f"Error creating histogram: {e}")
            return None, None
        
        # Create percentiles chart
        self._ensure_chinese_font()  # 重新确保字体设置
        fig2, ax2 = plt.subplots(figsize=(10, 6))
        
        try:
            # Calculate percentiles
            percentiles = [0, 10, 25, 50, 75, 90, 99, 100]
            values = [clean_series.quantile(p/100) for p in percentiles]
            labels = ['最小值', '10%', '25%', '50%\n(中位数)', '75%', '90%', '99%', '最大值']
            
            # Create bar chart
            bars = ax2.bar(labels, values, color='lightblue', edgecolor='navy', alpha=0.8, linewidth=1.5)
            
            # Add value labels on bars
            for bar, value in zip(bars, values):
                height = bar.get_height()
                ax2.text(bar.get_x() + bar.get_width()/2., height + height*0.02,
                        f'{value:.1f}', ha='center', va='bottom', fontsize=11, fontweight='bold')
            
            # 设置标题和轴标签
            ax2.set_title(f'{column_name} - 百分位数分布', fontsize=16, fontweight='bold')
            ax2.set_xlabel('百分位数', fontsize=14)
            ax2.set_ylabel(f'{column_name} 数值', fontsize=14)
            ax2.tick_params(axis='x', rotation=0, labelsize=12)
            ax2.tick_params(axis='y', labelsize=12)
            ax2.grid(True, alpha=0.3, axis='y')
            
            plt.tight_layout()
            
            # Save to memory
            percentile_buffer = io.BytesIO()
            plt.savefig(percentile_buffer, format='png', bbox_inches='tight', dpi=150,
                       facecolor='white', edgecolor='none')
            percentile_buffer.seek(0)
            plt.close()
            
            return hist_buffer, percentile_buffer
            
        except Exception as e:
            plt.close()
            print(f"Error creating percentiles chart: {e}")
            return hist_buffer, None
    
    def create_categorical_plot_for_ppt(self, series: pd.Series, column_name: str) -> io.BytesIO:
        """Create categorical analysis chart - returns in-memory image."""
        try:
            # 确保中文字体设置
            self._ensure_chinese_font()
            
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 7))
            
            # Count plot
            top_categories = series.value_counts().head(10)
            if len(top_categories) > 0:
                # 左侧图：计数条形图
                bars = ax1.barh(range(len(top_categories)), top_categories.values, 
                               color='lightcoral', edgecolor='darkred', alpha=0.8)
                ax1.set_yticks(range(len(top_categories)))
                ax1.set_yticklabels(top_categories.index, fontsize=11)
                ax1.set_title(f'前{len(top_categories)}个类别计数', fontsize=14, fontweight='bold')
                ax1.set_xlabel('计数', fontsize=12)
                ax1.tick_params(axis='x', labelsize=11)
                ax1.grid(True, alpha=0.3, axis='x')
                
                # Add value labels
                for i, (bar, value) in enumerate(zip(bars, top_categories.values)):
                    ax1.text(value + max(top_categories.values)*0.01, i, str(value), 
                            va='center', fontsize=10, fontweight='bold')
                
                # 右侧图：百分比
                percentages = (top_categories / len(series) * 100)
                bars2 = ax2.barh(range(len(percentages)), percentages.values, 
                                color='lightgreen', edgecolor='darkgreen', alpha=0.8)
                ax2.set_yticks(range(len(percentages)))
                ax2.set_yticklabels(percentages.index, fontsize=11)
                ax2.set_title(f'前{len(percentages)}个类别百分比', fontsize=14, fontweight='bold')
                ax2.set_xlabel('百分比 (%)', fontsize=12)
                ax2.tick_params(axis='x', labelsize=11)
                ax2.grid(True, alpha=0.3, axis='x')
                
                # Add percentage labels
                for i, (bar, value) in enumerate(zip(bars2, percentages.values)):
                    ax2.text(value + max(percentages.values)*0.01, i, f'{value:.1f}%', 
                            va='center', fontsize=10, fontweight='bold')
            
            plt.suptitle(f'{column_name} - 分类变量分析', fontsize=16, fontweight='bold')
            plt.tight_layout()
            
            # Save to memory
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150,
                       facecolor='white', edgecolor='none')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            plt.close()
            print(f"Error creating categorical plot: {e}")
            return None
    
    def create_missing_values_summary(self, df: pd.DataFrame) -> io.BytesIO:
        """Create missing values summary chart - returns in-memory image."""
        try:
            # 确保中文字体设置
            self._ensure_chinese_font()
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            missing_counts = df.isnull().sum()
            missing_counts = missing_counts[missing_counts > 0].sort_values(ascending=True)
            
            if len(missing_counts) > 0:
                bars = ax.barh(range(len(missing_counts)), missing_counts.values, 
                              color='salmon', edgecolor='darkred', alpha=0.8)
                ax.set_yticks(range(len(missing_counts)))
                ax.set_yticklabels(missing_counts.index, fontsize=12)
                ax.set_title('各列缺失值统计', fontsize=16, fontweight='bold')
                ax.set_xlabel('缺失值数量', fontsize=14)
                ax.set_ylabel('列名', fontsize=14)
                ax.tick_params(axis='both', labelsize=11)
                ax.grid(True, alpha=0.3, axis='x')
                
                # Add percentage labels
                total_rows = len(df)
                for i, (bar, value) in enumerate(zip(bars, missing_counts.values)):
                    percentage = (value / total_rows) * 100
                    ax.text(value + max(missing_counts.values)*0.01, i, 
                           f'{value} ({percentage:.1f}%)', 
                           va='center', fontsize=10, fontweight='bold')
            else:
                ax.text(0.5, 0.5, '✅ 数据集无缺失值', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=20, fontweight='bold',
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="lightgreen", alpha=0.7))
                ax.set_title('缺失值统计', fontsize=16, fontweight='bold')
                ax.set_xlabel('无缺失值', fontsize=14)
            
            plt.tight_layout()
            
            # Save to memory
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150,
                       facecolor='white', edgecolor='none')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            plt.close()
            print(f"Error creating missing values plot: {e}")
            return None