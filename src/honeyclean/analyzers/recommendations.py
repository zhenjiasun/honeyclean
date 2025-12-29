"""
Generate intelligent data cleaning recommendations.
"""

import pandas as pd
from typing import Dict, Any, List


class DataCleaningRecommendations:
    """Generate intelligent data cleaning recommendations.  生成智能数据清洗建议。"""

    @staticmethod
    def get_numeric_recommendations(analysis: Dict[str, Any]) -> List[str]:
        """Get cleaning recommendations for numeric columns. 获取数值列的清洗建议。"""
        recommendations = []

        # Check if analysis has error
        if "error" in analysis:
            zh = f"分析错误: {analysis['error']}"
            en = f"Analysis error: {analysis['error']}"
            recommendations.append((zh, en))
            return recommendations

        # Missing values - use .get() with default value
        missing_pct = analysis.get("missing_percentage", 0)
        if missing_pct > 5:
            zh = f"🔍 高缺失值 ({missing_pct:.1f}%)，建议使用中位数插值或高级方法进行处理"
            en = f"🔍 High missing values ({missing_pct:.1f}%). Consider imputation with median or advanced methods."
            recommendations.append((zh, en))

        # Outliers
        zscore_outliers = analysis.get("zscore_outliers", 0)
        if zscore_outliers > 0:
            zh = f"⚠️ 使用Z-score方法发现 {zscore_outliers} 个异常值，建议进行调查或删除处理"
            en = f"⚠️ Found {zscore_outliers} outliers using Z-score method. Consider investigation or removal."
            recommendations.append((zh, en))

        iqr_outliers = analysis.get("iqr_outliers", 0)
        if iqr_outliers > 0:
            zh = f"📊 使用IQR方法发现 {iqr_outliers} 个异常值，建议进行缩尾处理或转换"
            en = f"📊 Found {iqr_outliers} outliers using IQR method. Consider winsorization or transformation."
            recommendations.append((zh, en))

        # Skewness
        skewness = analysis.get("skewness", 0)
        if abs(skewness) > 2:
            zh = f"📈 高偏度 ({skewness:.2f})，建议进行对数变换或Box-Cox变换"
            en = f"📈 High skewness ({skewness:.2f}). Consider log transformation or Box-Cox transformation."
            recommendations.append((zh, en))

        # Distribution
        if not analysis.get("is_normal", True):
            zh = "📉 数据非正态分布，参数检验时建议进行变换处理"
            en = "📉 Data is not normally distributed. Consider transformation for parametric tests."
            recommendations.append((zh, en))

        # High coefficient of variation
        cv = analysis.get("coefficient_of_variation", 0)
        if cv > 1:
            zh = f"📊 高变异性 (CV = {cv:.2f})，建议进行标准化或归一化处理"
            en = f"📊 High variability (CV = {cv:.2f}). Consider normalization or standardization."
            recommendations.append((zh, en))

        return recommendations

    @staticmethod
    def get_categorical_recommendations(analysis: Dict[str, Any]) -> List[str]:
        """Get cleaning recommendations for categorical columns.
        获取分类列的清洗建议
        Returns list of (chinese, english) tuples
        """
        recommendations = []

        # Check if analysis has error
        if "error" in analysis:
            zh = f"分析错误: {analysis['error']}"
            en = f"Analysis error: {analysis['error']}"
            recommendations.append((zh, en))
            return recommendations

        # Missing values
        missing_pct = analysis.get("missing_percentage", 0)
        if missing_pct > 5:
            zh = f"🔍 高缺失值 ({missing_pct:.1f}%)，建议创建'未知'类别或使用众数填充"
            en = f"🔍 High missing values ({missing_pct:.1f}%). Consider creating 'Unknown' category or mode imputation."
            recommendations.append((zh, en))

        # High cardinality
        if analysis.get("is_high_cardinality", False):
            unique_count = analysis.get("unique_count", 0)
            zh = f"📊 高基数 ({unique_count} 个唯一值)，建议对稀有类别进行分组或使用目标编码"
            en = f"📊 High cardinality ({unique_count} unique values). Consider grouping rare categories or target encoding."
            recommendations.append((zh, en))

        # Rare categories
        rare_categories = analysis.get("rare_categories", [])
        if rare_categories:
            zh = f"🏷️ 发现 {len(rare_categories)} 个稀有类别，建议分组为'其他'类别"
            en = f"🏷️ Found {len(rare_categories)} rare categories. Consider grouping into 'Other' category."
            recommendations.append((zh, en))

        # Imbalanced categories
        value_counts = analysis.get("value_counts", {})
        if value_counts and len(value_counts) > 1:
            max_count = max(value_counts.values())
            min_count = min(value_counts.values())
            if max_count / min_count > 10:
                zh = "⚖️ 类别高度不平衡，建模时建议考虑重采样或加权处理"
                en = "⚖️ Highly imbalanced categories. Consider resampling or weighting for modeling."
                recommendations.append((zh, en))

        return recommendations

    @staticmethod
    def get_datetime_recommendations(analysis: Dict[str, Any]) -> List[str]:
        """Get cleaning recommendations for datetime columns. 获取日期时间列的清洗建议。"""
        recommendations = []

        # Check if analysis has error
        if "error" in analysis:
            zh = f"分析错误: {analysis['error']}"
            en = f"Analysis error: {analysis['error']}"
            recommendations.append((zh, en))
            return recommendations

        # Missing values
        missing_pct = analysis.get("missing_percentage", 0)
        if missing_pct > 5:
            zh = f"🔍 高缺失值 ({missing_pct:.1f}%)，建议使用前向填充或插值处理"
            en = f"🔍 High missing values ({missing_pct:.1f}%). Consider forward-fill or interpolation."
            recommendations.append((zh, en))

        # Date range
        year_range = analysis.get("year_range", 0)
        if year_range > 50:
            zh = "📅 日期范围过宽，请验证所有日期的有效性并考虑过滤异常值"
            en = "📅 Wide date range. Verify if all dates are valid and consider filtering outliers."
            recommendations.append((zh, en))

        # Feature extraction
        zh = "🔧 建议提取特征：年、月、日、星期、季节、季度"
        en = "🔧 Consider extracting features: year, month, day, weekday, season, quarter."
        recommendations.append((zh, en))

        return recommendations

    @staticmethod
    def get_general_recommendations(df: pd.DataFrame) -> List[str]:
        """Get general dataset recommendations."""
        recommendations = []

        try:
            # Dataset size
            if len(df) < 100:
                zh = "📏 数据集较小，建议收集更多数据以进行稳健分析"
                en = "📏 Small dataset. Consider collecting more data for robust analysis."
            elif len(df) > 1000000:
                zh = "📊 大数据集，建议使用采样或分块处理以提高内存效率"
                en = "📊 Large dataset. Consider sampling or chunking for memory efficiency."
                recommendations.append((zh, en))

            # Memory usage
            memory_mb = df.memory_usage(deep=True).sum() / 1024 / 1024
            if memory_mb > 1000:
                zh = f"💾 高内存使用 ({memory_mb:.1f} MB)，建议优化数据类型或分块处理"
                en = f"💾 High memory usage ({memory_mb:.1f} MB). Consider optimizing data types or processing in chunks."
                recommendations.append((zh, en))

            # Duplicate rows
            duplicate_count = df.duplicated().sum()
            if duplicate_count > 0:
                zh = f"🔄 发现 {duplicate_count} 个重复行，建议删除重复数据"
                en = f"🔄 Found {duplicate_count} duplicate rows. Consider removing duplicates."
                recommendations.append((zh, en))

        except Exception as e:
            zh = f"常规分析错误: {str(e)}"
            en = f"Error in general analysis: {str(e)}"
            recommendations.append((zh, en))

        return recommendations
