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
    
    def create_enhanced_numeric_plot_for_ppt(self, series: pd.Series, column_name: str) -> Tuple[io.BytesIO, io.BytesIO]:
        """Create enhanced histogram and percentiles chart for PPT - returns original format."""
        # Use the original method that returns both plots
        return self.create_numeric_plot_for_ppt(series, column_name)
    
    def create_correlation_plot_for_ppt(self, df: pd.DataFrame, feature_col: str, target_col: str) -> io.BytesIO:
        """Create correlation scatter plot between feature and target for PPT."""
        try:
            self._ensure_chinese_font()
            
            # Only use numeric columns for correlation
            if not (pd.api.types.is_numeric_dtype(df[feature_col]) and pd.api.types.is_numeric_dtype(df[target_col])):
                return None
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            # Remove missing values
            clean_df = df[[feature_col, target_col]].dropna()
            
            if len(clean_df) == 0:
                return None
            
            # Scatter plot
            ax.scatter(clean_df[feature_col], clean_df[target_col], alpha=0.6, s=50, color='steelblue')
            
            # Add trend line
            z = np.polyfit(clean_df[feature_col], clean_df[target_col], 1)
            p = np.poly1d(z)
            ax.plot(clean_df[feature_col], p(clean_df[feature_col]), "r--", alpha=0.8, linewidth=2)
            
            # Calculate correlation
            corr_coef = clean_df[feature_col].corr(clean_df[target_col])
            r_squared = corr_coef ** 2
            
            # Add correlation info
            ax.text(0.05, 0.95, f'相关系数: {corr_coef:.4f}\nR²: {r_squared:.4f}', 
                   transform=ax.transAxes, fontsize=12, verticalalignment='top',
                   bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.8))
            
            ax.set_title(f'{feature_col} vs {target_col} - 相关性分析', fontsize=14, fontweight='bold')
            ax.set_xlabel(feature_col, fontsize=12)
            ax.set_ylabel(target_col, fontsize=12)
            ax.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150,
                       facecolor='white', edgecolor='none')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            plt.close()
            print(f"Error creating correlation plot: {e}")
            return None
    
    def create_feature_correlation_heatmap_for_ppt(self, df: pd.DataFrame, feature_col: str, top_n: int = 5) -> io.BytesIO:
        """Create heatmap showing correlations between feature and top N most correlated features for PPT."""
        try:
            self._ensure_chinese_font()
            
            # Only use numeric columns
            numeric_df = df.select_dtypes(include=[np.number])
            
            if feature_col not in numeric_df.columns or len(numeric_df.columns) < 2:
                return None
            
            # Calculate correlations with the feature
            correlations = numeric_df.corr()[feature_col].abs().sort_values(ascending=False)
            
            # Get top N correlations (excluding self-correlation)
            top_correlations = correlations.drop(feature_col).head(top_n)
            
            if len(top_correlations) == 0:
                return None
            
            # Create correlation matrix for these features
            selected_features = [feature_col] + list(top_correlations.index)
            corr_matrix = numeric_df[selected_features].corr()
            
            # Create a more compact, square figure
            fig, ax = plt.subplots(figsize=(8, 6))
            
            # Create heatmap without mask for better visibility
            sns.heatmap(corr_matrix, annot=True, cmap='RdYlBu_r', center=0,
                       square=True, ax=ax, cbar_kws={'shrink': 0.8}, fmt='.3f',
                       linewidths=0.5, linecolor='white')
            
            ax.set_title(f'{feature_col} - 前{top_n}个相关特征热图', fontsize=12, fontweight='bold')
            
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150,
                       facecolor='white', edgecolor='none')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            plt.close()
            print(f"Error creating heatmap: {e}")
            return None
    
    def create_enhanced_categorical_plot_for_ppt(self, series: pd.Series, column_name: str) -> io.BytesIO:
        """Create enhanced categorical plot with value counts and percentages for PPT."""
        try:
            self._ensure_chinese_font()
            
            fig, ax = plt.subplots(figsize=(14, 8))
            
            # Get top categories
            top_categories = series.value_counts().head(15)
            
            if len(top_categories) == 0:
                return None
            
            # Create horizontal bar plot
            bars = ax.barh(range(len(top_categories)), top_categories.values, 
                          color='lightcoral', edgecolor='darkred', alpha=0.8)
            
            ax.set_yticks(range(len(top_categories)))
            ax.set_yticklabels([str(cat)[:30] + '...' if len(str(cat)) > 30 else str(cat) 
                               for cat in top_categories.index], fontsize=10)
            
            # Add value and percentage labels
            total_count = len(series)
            for i, (bar, value) in enumerate(zip(bars, top_categories.values)):
                percentage = (value / total_count) * 100
                ax.text(value + max(top_categories.values)*0.01, i, 
                       f'{value} ({percentage:.1f}%)', 
                       va='center', fontsize=9, fontweight='bold')
            
            ax.set_title(f'{column_name} - 类别分布 (前{len(top_categories)}类)', fontsize=14, fontweight='bold')
            ax.set_xlabel('计数', fontsize=12)
            ax.grid(True, alpha=0.3, axis='x')
            
            # Add statistics text
            unique_count = series.nunique()
            cardinality = unique_count / len(series)
            stats_text = f'统计信息:\n总类别数: {unique_count}\n基数: {cardinality:.3f}\n显示: 前{len(top_categories)}类'
            ax.text(0.98, 0.02, stats_text, transform=ax.transAxes, fontsize=10,
                   verticalalignment='bottom', horizontalalignment='right',
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
            
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=150,
                       facecolor='white', edgecolor='none')
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            plt.close()
            print(f"Error creating enhanced categorical plot: {e}")
            return None
    
    def create_categorical_target_analysis_for_ppt(self, df: pd.DataFrame, feature_col: str, target_col: str) -> io.BytesIO:
        """Create categorical feature vs target analysis for PPT."""
        try:
            self._ensure_chinese_font()
            
            # 首先获取前10个最常见的类别
            top_categories = df[feature_col].value_counts().head(10).index.tolist()
        
            # 过滤数据，只保留前10个类别
            df_filtered = df[df[feature_col].isin(top_categories)].copy()

            # Create cross-tabulation
            crosstab = pd.crosstab(df_filtered[feature_col], df_filtered[target_col], normalize='index') * 100
            
            # 确保按照原始频率顺序排列
            crosstab = crosstab.reindex(top_categories)
            
            if crosstab.empty:
                return None
            
            # 增加图片尺寸和DPI以提高清晰度
            fig, ax = plt.subplots(figsize=(16, 8))  # 增加高度以适应更好的显示
            
            # Create stacked bar plot with better styling
            crosstab.plot(kind='barh', stacked=True, ax=ax, 
                        colormap='Set3', alpha=0.9, width=0.7)
            
            # 优化标题和标签字体大小
            ax.set_title(f'{feature_col} vs {target_col} - 分类交叉分析 (前10个类别)', 
                        fontsize=18, fontweight='bold', pad=20)
            ax.set_xlabel('百分比 (%)', fontsize=14, fontweight='bold')
            ax.set_ylabel(feature_col, fontsize=14, fontweight='bold')
            
            # 优化图例
            ax.legend(title=target_col, bbox_to_anchor=(1.02, 1), loc='upper left',
                    fontsize=12, title_fontsize=13)
            
            # 优化网格和刻度
            ax.grid(True, alpha=0.4, axis='x', linestyle='--')
            ax.tick_params(axis='both', which='major', labelsize=12)
            
            # 限制Y轴标签长度，避免过长
            y_labels = [str(label)[:20] + '...' if len(str(label)) > 20 else str(label) 
                    for label in ax.get_yticklabels()]
            ax.set_yticklabels(y_labels)
            
            # 添加数值标签（只在较大的区块上显示）
            for container in ax.containers:
                ax.bar_label(container, 
                            labels=[f'{v:.1f}%' if v > 8 else '' for v in container.datavalues], 
                            label_type='center', fontsize=10, fontweight='bold', color='white')
            
            plt.tight_layout()
            
            buffer = io.BytesIO()
            plt.savefig(buffer, format='png', bbox_inches='tight', dpi=300,
                    facecolor='white', edgecolor='none', pad_inches=0.1)
            buffer.seek(0)
            plt.close()
            
            return buffer
            
        except Exception as e:
            plt.close()
            print(f"Error creating categorical target analysis: {e}")
            return None