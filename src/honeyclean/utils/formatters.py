"""
Utility functions for formatting statistical output into readable tables.
"""

from typing import Dict, Any
try:
    from tabulate import tabulate
except ImportError:
    def tabulate(data, headers=None, tablefmt="grid", floatfmt=".4f"):
        """Fallback tabulate function if tabulate is not installed."""
        if not data:
            return "No data to display"
        
        result = []
        if headers:
            result.append(" | ".join(str(h) for h in headers))
            result.append("-" * 50)
        
        for row in data:
            result.append(" | ".join(str(cell) for cell in row))
        
        return "\n".join(result)


class StatisticalFormatter:
    """Formats statistical analysis results into well-structured tables."""
    
    @staticmethod
    def format_numeric_stats(stats: Dict[str, Any]) -> str:
        """Format numeric statistics into a clean table."""
        if 'error' in stats:
            return f"Error: {stats['error']}"
        
        # Basic statistics table
        basic_stats = [
            ["Count (计数)", f"{stats.get('count', 'N/A'):,}"],
            ["Missing (缺失值)", f"{stats.get('missing_count', 'N/A'):,} ({stats.get('missing_percentage', 0):.2f}%)"],
            ["Mean (平均数)", f"{stats.get('mean', 0):.4f}"],
            ["Median (中位数)", f"{stats.get('median', 0):.4f}"],
            ["Mode (众数)", f"{stats.get('mode', 'N/A')}"],
            ["Std Dev (标准差)", f"{stats.get('std', 0):.4f}"],
            ["Min (最小值)", f"{stats.get('min', 0):.4f}"],
            ["Max (最大值)", f"{stats.get('max', 0):.4f}"],
            ["Range (范围)", f"{stats.get('range', 0):.4f}"],
        ]
        
        # Distribution statistics table
        distribution_stats = [
            ["Q1 (第一四分位数)", f"{stats.get('q1', 0):.4f}"],
            ["Q3 (第三四分位数)", f"{stats.get('q3', 0):.4f}"],
            ["IQR (四分位距)", f"{stats.get('iqr', 0):.4f}"],
            ["Skewness (偏度)", f"{stats.get('skewness', 0):.4f}"],
            ["Kurtosis (峰度)", f"{stats.get('kurtosis', 0):.4f}"],
            ["CV (变异系数)", f"{stats.get('coefficient_of_variation', 0):.4f}"],
        ]
        
        # Outlier detection table
        outlier_stats = [
            ["Z-Score Outliers (Z分数异常值)", f"{stats.get('zscore_outliers', 0):,} ({stats.get('zscore_percentage', 0):.2f}%)"],
            ["IQR Outliers (四分位距异常值)", f"{stats.get('iqr_outliers', 0):,} ({stats.get('iqr_percentage', 0):.2f}%)"],
            ["Modified Z-Score (修正Z分数)", f"{stats.get('modified_zscore_outliers', 0):,} ({stats.get('modified_zscore_percentage', 0):.2f}%)"],
            ["IQR Bounds (四分位距边界)", f"[{stats.get('iqr_lower_bound', 0):.2f}, {stats.get('iqr_upper_bound', 0):.2f}]"],
        ]
        
        # Distribution tests table  
        distribution_tests = []
        if stats.get('shapiro_p_value') is not None:
            distribution_tests.append(["Shapiro-Wilk p-value (夏皮罗检验p值)", f"{stats.get('shapiro_p_value', 0):.6f}"])
            distribution_tests.append(["Is Normal (是否正态分布)", "Yes (是)" if stats.get('is_normal', False) else "No (否)"])
        if stats.get('dagostino_p_value') is not None:
            distribution_tests.append(["D'Agostino p-value (达戈斯蒂诺检验p值)", f"{stats.get('dagostino_p_value', 0):.6f}"])
        
        # Format all tables
        result = "📊 NUMERIC STATISTICS (数值统计)\n" + "="*50 + "\n\n"
        
        result += "📈 Basic Statistics (基础统计):\n"
        result += tabulate(basic_stats, headers=["Metric (指标)", "Value (值)"], tablefmt="grid", floatfmt=".4f") + "\n\n"
        
        result += "📊 Distribution Statistics (分布统计):\n"  
        result += tabulate(distribution_stats, headers=["Metric (指标)", "Value (值)"], tablefmt="grid", floatfmt=".4f") + "\n\n"
        
        result += "🔍 Outlier Detection (异常值检测):\n"
        result += tabulate(outlier_stats, headers=["Method (方法)", "Count (%) (数量百分比)"], tablefmt="grid") + "\n\n"
        
        if distribution_tests:
            result += "🧪 Distribution Tests (分布检验):\n"
            result += tabulate(distribution_tests, headers=["Test (检验)", "Result (结果)"], tablefmt="grid") + "\n\n"
        
        return result
    
    @staticmethod
    def format_categorical_stats(stats: Dict[str, Any]) -> str:
        """Format categorical statistics into a clean table."""
        if 'error' in stats:
            return f"Error: {stats['error']}"
        
        # Basic statistics table
        basic_stats = [
            ["Count (计数)", f"{stats.get('count', 'N/A'):,}"],
            ["Missing (缺失值)", f"{stats.get('missing_count', 'N/A'):,} ({stats.get('missing_percentage', 0):.2f}%)"],
            ["Unique Values (唯一值)", f"{stats.get('unique_count', 'N/A'):,}"],
            ["Cardinality (基数)", f"{stats.get('cardinality', 0):.4f}"],
            ["Mode (众数)", f"{stats.get('mode', 'N/A')}"],
            ["High Cardinality (高基数)", "Yes (是)" if stats.get('is_high_cardinality', False) else "No (否)"],
        ]
        
        # Top values table
        value_counts = stats.get('value_counts', {})
        value_percentages = stats.get('value_percentages', {})
        
        top_values = []
        for value, count in list(value_counts.items())[:10]:
            percentage = value_percentages.get(value, 0)
            top_values.append([str(value)[:30], f"{count:,}", f"{percentage:.2f}%"])
        
        # Rare categories
        rare_categories = stats.get('rare_categories', [])
        rare_count = len(rare_categories)
        
        result = "📊 CATEGORICAL STATISTICS (分类统计)\n" + "="*50 + "\n\n"
        
        result += "📈 Basic Statistics (基础统计):\n"
        result += tabulate(basic_stats, headers=["Metric (指标)", "Value (值)"], tablefmt="grid") + "\n\n"
        
        if top_values:
            result += "🔝 Top 10 Values (前10高频值):\n"
            result += tabulate(top_values, headers=["Value (值)", "Count (计数)", "Percentage (百分比)"], tablefmt="grid") + "\n\n"
        
        if rare_count > 0:
            result += f"🔍 Rare Categories (稀有类别) ({rare_count} found):\n"
            rare_display = rare_categories[:10] if len(rare_categories) > 10 else rare_categories
            for category in rare_display:
                result += f"  • {category}\n"
            if len(rare_categories) > 10:
                result += f"  ... and {len(rare_categories) - 10} more\n"
            result += "\n"
        
        return result
    
    @staticmethod
    def format_datetime_stats(stats: Dict[str, Any]) -> str:
        """Format datetime statistics into a clean table."""
        if 'error' in stats:
            return f"Error: {stats['error']}"
        
        # Basic statistics table
        basic_stats = [
            ["Count (计数)", f"{stats.get('count', 'N/A'):,}"],
            ["Missing (缺失值)", f"{stats.get('missing_count', 'N/A'):,} ({stats.get('missing_percentage', 0):.2f}%)"],
            ["Min Date (最早日期)", f"{stats.get('min_date', 'N/A')}"],
            ["Max Date (最晚日期)", f"{stats.get('max_date', 'N/A')}"],
            ["Date Range (日期范围)", f"{stats.get('date_range', 'N/A')}"],
            ["Year Range (年份范围)", f"{stats.get('year_range', 'N/A')} years (年)"],
            ["Unique Years (唯一年份)", f"{stats.get('unique_years', 'N/A'):,}"],
            ["Unique Months (唯一月份)", f"{stats.get('unique_months', 'N/A'):,}"],
        ]
        
        # Weekday distribution table
        weekday_dist = stats.get('weekday_distribution', {})
        weekday_table = [[day, f"{count:,}"] for day, count in weekday_dist.items()]
        
        # Month distribution table  
        month_dist = stats.get('month_distribution', {})
        month_table = [[month, f"{count:,}"] for month, count in month_dist.items()]
        
        result = "📊 DATETIME STATISTICS (日期时间统计)\n" + "="*50 + "\n\n"
        
        result += "📈 Basic Statistics (基础统计):\n"
        result += tabulate(basic_stats, headers=["Metric (指标)", "Value (值)"], tablefmt="grid") + "\n\n"
        
        if weekday_table:
            result += "📅 Weekday Distribution (星期分布):\n"
            result += tabulate(weekday_table, headers=["Weekday (星期)", "Count (计数)"], tablefmt="grid") + "\n\n"
        
        if month_table:
            result += "📆 Month Distribution (月份分布):\n"
            result += tabulate(month_table, headers=["Month (月份)", "Count (计数)"], tablefmt="grid") + "\n\n"
        
        return result
    
    @staticmethod
    def format_correlation_analysis(correlations: Dict[str, Any], target_col: str) -> str:
        """Format correlation analysis results with target column."""
        if not correlations:
            return "No correlation analysis available\n"
        
        result = f"🎯 CORRELATION WITH TARGET (与目标变量的相关性): {target_col}\n" + "="*50 + "\n\n"
        
        # Sort correlations by absolute value
        sorted_corrs = sorted(correlations.items(), key=lambda x: abs(x[1]), reverse=True)
        
        corr_table = []
        for col, corr_val in sorted_corrs:
            if col != target_col:  # Exclude self-correlation
                strength = StatisticalFormatter._interpret_correlation(abs(corr_val))
                corr_table.append([col[:30], f"{corr_val:.4f}", strength])
        
        if corr_table:
            result += tabulate(corr_table, headers=["Feature (特征)", "Correlation (相关性)", "Strength (强度)"], tablefmt="grid") + "\n\n"
        else:
            result += "No correlations found (未找到相关性)\n\n"
        
        return result
    
    @staticmethod
    def format_target_distribution(target_stats: Dict[str, Any], target_col: str) -> str:
        """Format target column distribution analysis."""
        result = f"🎯 TARGET DISTRIBUTION (目标变量分布): {target_col}\n" + "="*50 + "\n\n"
        
        if target_stats.get('type') == 'categorical':
            value_counts = target_stats.get('value_counts', {})
            value_percentages = target_stats.get('value_percentages', {})
            
            dist_table = []
            for value, count in value_counts.items():
                percentage = value_percentages.get(value, 0)
                dist_table.append([str(value)[:30], f"{count:,}", f"{percentage:.2f}%"])
            
            if dist_table:
                result += "📊 Category Distribution (类别分布):\n"
                result += tabulate(dist_table, headers=["Category (类别)", "Count (计数)", "Percentage (百分比)"], tablefmt="grid") + "\n\n"
        
        elif target_stats.get('type') == 'numeric':
            # For numeric targets, show distribution statistics
            result += StatisticalFormatter.format_numeric_stats(target_stats)
        
        return result
    
    @staticmethod
    def format_id_uniqueness_check(id_results: Dict[str, Dict[str, Any]]) -> str:
        """Format ID column uniqueness check results."""
        if not id_results:
            return "No ID columns configured\n"
        
        result = "🆔 ID COLUMNS UNIQUENESS CHECK (ID列唯一性检查)\n" + "="*50 + "\n\n"
        
        uniqueness_table = []
        for col, stats in id_results.items():
            total_count = stats.get('total_count', 0)
            unique_count = stats.get('unique_count', 0)
            duplicate_count = stats.get('duplicate_count', 0)
            uniqueness_pct = stats.get('uniqueness_percentage', 0)
            
            status = "✅ Unique (唯一)" if duplicate_count == 0 else f"❌ {duplicate_count:,} duplicates (重复)"
            
            uniqueness_table.append([
                col[:25],
                f"{total_count:,}",
                f"{unique_count:,}",
                f"{uniqueness_pct:.2f}%", 
                status
            ])
        
        result += tabulate(uniqueness_table, 
                          headers=["ID Column (ID列)", "Total (总数)", "Unique (唯一)", "Uniqueness % (唯一性%)", "Status (状态)"], 
                          tablefmt="grid") + "\n\n"
        
        return result
    
    @staticmethod
    def _interpret_correlation(abs_corr: float) -> str:
        """Interpret correlation strength."""
        if abs_corr >= 0.8:
            return "Very Strong (很强)"
        elif abs_corr >= 0.6:
            return "Strong (强)"
        elif abs_corr >= 0.4:
            return "Moderate (中等)"
        elif abs_corr >= 0.2:
            return "Weak (弱)"
        else:
            return "Very Weak (很弱)"