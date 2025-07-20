# HoneyClean 🍯 (蜂蜜清洁)

**Automated Data Profiling and Cleaning Package (自动化数据分析和清洗包)**

HoneyClean is a comprehensive Python package for automated data profiling, cleaning recommendations, and professional report generation. It provides intelligent analysis of datasets with actionable insights for data scientists and analysts.

HoneyClean 是一个全面的 Python 包，用于自动化数据分析、清洗建议和专业报告生成。它为数据科学家和分析师提供智能的数据集分析和可行的洞察。

## ✨ Features (功能特性)

### 🔍 **Comprehensive Data Analysis (全面数据分析)**
- **Automatic type detection (自动类型检测)**: Smart inference of numeric, categorical, datetime, and text data types
- **Statistical analysis (统计分析)**: Comprehensive statistics including distribution analysis, outlier detection, and correlation analysis
- **Missing value analysis (缺失值分析)**: Detailed missing data patterns and recommendations
- **Duplicate detection (重复检测)**: Identification of duplicate rows and values

### 🎯 **Target Variable Analysis (目标变量分析)**
- **Correlation analysis (相关性分析)**: Feature-target correlation with strength interpretation
- **Target distribution (目标分布)**: Analysis of target variable distribution patterns
- **Categorical cross-analysis (分类交叉分析)**: Category distribution by target values
- **Multiple target support (多目标支持)**: Handle multiple target variables simultaneously

### 🆔 **ID Column Validation (ID列验证)**
- **Uniqueness checking (唯一性检查)**: Validate ID column uniqueness
- **Composite ID support (复合ID支持)**: Multi-column ID validation
- **Duplicate detection (重复检测)**: Identify and report duplicate ID values

### 📊 **Enhanced Formatting (增强格式化)**
- **Bilingual output (双语输出)**: English and Chinese labels in all reports
- **Table formatting (表格格式化)**: Clean, readable statistical tables
- **Professional styling (专业样式)**: Well-organized output with clear sections

### 📋 **Intelligent Recommendations (智能建议)**
- **Type-specific suggestions (类型特定建议)**: Customized cleaning recommendations for each data type
- **Actionable insights (可执行洞察)**: Practical data quality improvement suggestions
- **Priority-based recommendations (优先级建议)**: Ranked suggestions by importance

### 📑 **Professional Reports (专业报告)**
- **PowerPoint generation (PowerPoint生成)**: Automated creation of presentation-ready reports
- **JSON exports (JSON导出)**: Machine-readable analysis results
- **CSV summaries (CSV摘要)**: Quick overview tables
- **Chinese language support (中文支持)**: Full Chinese interface in reports

### ⚙️ **Configurable & Flexible (可配置和灵活)**
- **TOML configuration (TOML配置)**: Easy-to-edit configuration files
- **Command-line interface (命令行界面)**: User-friendly CLI tools
- **Jupyter integration (Jupyter集成)**: Seamless notebook support

## 🚀 Quick Start (快速开始)

### 1. Installation (安装)

```bash
# Clone the repository (克隆仓库)
git clone https://github.com/honeyclean/honeyclean.git
cd honeyclean

# Install package (安装包)
pip install -e .
```

### 2. Initialize Configuration (初始化配置)

```bash
# Create configuration file (创建配置文件)
honeyclean init

# This creates base.toml with default settings
# 这将创建包含默认设置的 base.toml 文件
```

### 3. Configure Your Analysis (配置您的分析)

Edit `base.toml` to customize your analysis settings (编辑 `base.toml` 来自定义分析设置):

```toml
[honeyclean]
version = "1.0.0"
description = "Automated data profiling and cleaning recommendations"

[paths]
# Set your data file path (设置数据文件路径)
input_data = "./your_data.csv"
# Set output directory (设置输出目录)
output_reports = "./reports"

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

[columns]
# IMPORTANT: Configure these for enhanced analysis
# 重要：配置这些以进行增强分析

# Target column(s) for correlation analysis (目标列用于相关性分析)
# Single target: target_col = "sales_amount"
# Multiple targets: target_col = ["target1", "target2"]
target_col = "your_target_column"

# ID columns for uniqueness checking (用于唯一性检查的ID列)
# id_cols = ["user_id", "transaction_id", "product_id"]
id_cols = ["your_id_column"]

[visualization]
figure_dpi = 300
figure_width = 12
figure_height = 8
color_palette = "husl"

[output]
generate_html = true
generate_json = true
generate_powerpoint = true
generate_csv_summary = true

[logging]
level = "INFO"
format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
file = "honeyclean.log"
```

### 4. Run Analysis (运行分析)

**Simple one-command analysis (简单一命令分析):**
```bash
# Complete analysis using config file settings (使用配置文件设置的完整分析)
honeyclean run

# Override settings if needed (需要时覆盖设置)
honeyclean run --sample 10000 --output ./custom_reports
```

**Individual commands (单独命令):**
```bash
# Basic profiling with reports (基础分析和报告)
honeyclean profile  # Uses config file
honeyclean profile your_data.csv  # Override with specific file

# Enhanced statistical display (增强统计显示)  
honeyclean stats  # Uses config file
honeyclean stats your_data.csv --target-col sales_amount

# Analyze specific columns only (仅分析特定列)
honeyclean analyze your_data.csv --columns col1 --columns col2

# Sample large datasets (对大数据集采样)
honeyclean run --sample 10000
```

## 📖 Command Reference (命令参考)

### `honeyclean init`
Create a new configuration file (创建新的配置文件)
```bash
honeyclean init                    # Create base.toml
honeyclean init --config my.toml   # Custom config file name
honeyclean init --force            # Overwrite existing config
```

### `honeyclean run` ⭐ **RECOMMENDED**
Complete analysis in one command (一键完整分析)
```bash
honeyclean run                     # Uses config file settings
honeyclean run data.csv            # Override input file
honeyclean run --sample 5000       # Sample large datasets
honeyclean run --output ./reports  # Custom output directory
honeyclean run --no-show-stats     # Skip detailed stats display
```

### `honeyclean profile`
Dataset profiling with report generation (数据集分析和报告生成)
```bash
honeyclean profile                 # Uses config file
honeyclean profile data.csv        # Override input file
honeyclean profile --format json   # Specific output format
honeyclean profile --sample 5000   # Sample large datasets
```

### `honeyclean stats`
Enhanced statistical analysis with embedded reports (增强统计分析和嵌入式报告)
```bash
honeyclean stats                   # Generate reports with embedded stats
honeyclean stats --console         # Also display stats in terminal
honeyclean stats data.csv --target-col revenue --id-cols user_id
honeyclean stats --output ./reports # Custom output directory
```

### `honeyclean analyze`
Detailed column-specific analysis (详细的列特定分析)
```bash
honeyclean analyze data.csv --columns price --columns quantity
honeyclean analyze data.csv --output ./column_analysis
```

### `honeyclean info`
Display current configuration (显示当前配置)
```bash
honeyclean info
```

## 🔧 Configuration Guide (配置指南)

### Essential Configuration Steps (必要配置步骤):

1. **Set Data Path (设置数据路径)**
   ```toml
   [paths]
   input_data = "/path/to/your/data.csv"
   output_reports = "/path/to/output/directory"
   ```

2. **Configure Target Analysis (配置目标分析)**
   ```toml
   [columns]
   # For regression: numeric target
   target_col = "sales_amount"
   
   # For classification: categorical target
   target_col = "customer_category"
   
   # Multiple targets
   target_col = ["target1", "target2"]
   ```

3. **Configure ID Validation (配置ID验证)**
   ```toml
   [columns]
   # Single ID column
   id_cols = ["user_id"]
   
   # Multiple ID columns (composite key)
   id_cols = ["user_id", "session_id", "transaction_id"]
   ```

4. **Adjust Analysis Thresholds (调整分析阈值)**
   ```toml
   [thresholds]
   outlier_threshold = 3.0        # Z-score threshold for outliers
   correlation_threshold = 0.8     # High correlation threshold
   high_cardinality_threshold = 50 # High cardinality threshold
   missing_value_threshold = 0.05  # Missing value concern threshold
   ```

## 📊 Output Examples (输出示例)

### Statistical Tables (统计表格)
```
📊 NUMERIC STATISTICS (数值统计)
==================================================

📈 Basic Statistics (基础统计):
+------------------+----------+
| Metric (指标)    | Value (值) |
+==================+==========+
| Count (计数)     | 10,000   |
| Missing (缺失值) | 50 (0.5%)|
| Mean (平均数)    | 125.45   |
| Median (中位数)  | 120.30   |
+------------------+----------+

🎯 CORRELATION WITH TARGET (与目标变量的相关性): sales_amount
=============================================================

+----------------+-------------------+------------------+
| Feature (特征) | Correlation (相关性)| Strength (强度)  |
+================+===================+==================+
| price         | 0.8234            | Very Strong (很强)|
| quantity      | 0.6891            | Strong (强)      |
+----------------+-------------------+------------------+
```

### Report Files Generated (生成的报告文件)
- **PowerPoint Report**: Professional presentation with embedded bilingual statistics, target analysis, and ID validation
- **JSON Report**: Complete machine-readable results with formatted statistics sections
- **CSV Summary**: Quick overview table
- **Log File**: Detailed processing information

### Enhanced Report Content (增强报告内容)
**All reports now include (所有报告现在包括):**
- 📊 **Bilingual Statistics**: English/Chinese labels in all statistical tables
- 🎯 **Target Analysis**: Correlation analysis and distribution insights (if configured)
- 🆔 **ID Validation**: Uniqueness checking and duplicate detection (if configured)
- 💡 **Enhanced Recommendations**: Comprehensive data cleaning suggestions
- 📈 **Professional Formatting**: Clean, readable presentation suitable for stakeholders

## 🔬 Advanced Features (高级功能)

### Target Variable Analysis (目标变量分析)
- **Correlation Analysis**: Automatically calculates correlations between all features and target variables
- **Distribution Analysis**: Analyzes target distribution for class balance (classification) or normality (regression)
- **Cross-tabulation**: For categorical targets, shows how other categorical variables relate to target classes

### ID Column Validation (ID列验证)
- **Uniqueness Checking**: Validates that ID columns contain unique values
- **Composite Key Support**: Checks uniqueness across multiple ID columns
- **Duplicate Reporting**: Identifies and reports specific duplicate values

### Enhanced Statistics (增强统计)
- **Outlier Detection**: Multiple methods (Z-score, IQR, Modified Z-score)
- **Distribution Testing**: Normality tests (Shapiro-Wilk, D'Agostino)
- **Cardinality Analysis**: High cardinality detection for categorical variables

## 🛠️ Troubleshooting (故障排除)

### Common Issues (常见问题)

1. **Module Not Found Error**
   ```bash
   # Install missing dependencies
   pip install pandas numpy scipy matplotlib seaborn python-pptx click
   ```

2. **Memory Issues with Large Files**
   ```toml
   [analysis]
   chunk_size = 5000
   max_memory_mb = 512
   ```
   
   ```bash
   # Use sampling for large datasets
   honeyclean stats large_file.csv --sample 10000
   ```

3. **Configuration File Not Found**
   ```bash
   # Create configuration file first
   honeyclean init
   ```

4. **Permission Errors**
   ```bash
   # Check output directory permissions
   mkdir -p ./reports
   chmod 755 ./reports
   ```

## 📋 Example Workflow (示例工作流程)

### Simple Workflow (简单工作流程) ⭐ **RECOMMENDED**
```bash
# 1. Initialize project (初始化项目)
honeyclean init

# 2. Edit base.toml with your data path and target columns
# 编辑 base.toml，设置数据路径和目标列

# 3. Run complete analysis (运行完整分析)
honeyclean run

# That's it! All analysis, stats, and reports are generated with:
# 完成！所有分析、统计和报告都已生成，包含：
# ✅ Bilingual statistical tables embedded in reports
# ✅ Target correlation analysis (if configured)
# ✅ ID uniqueness validation (if configured)  
# ✅ Professional PowerPoint and JSON reports
```

### Advanced Workflow (高级工作流程)
```bash
# 1. Initialize and configure (初始化和配置)
honeyclean init
# Edit base.toml with your settings

# 2. Quick overview without reports (快速概览，无报告)
honeyclean stats

# 3. Generate detailed reports (生成详细报告)
honeyclean profile

# 4. Analyze specific problematic columns (分析特定问题列)
honeyclean analyze --columns price --columns category

# 5. Complete analysis with custom settings (自定义设置的完整分析)
honeyclean run --sample 50000 --output ./final_reports

# 6. Check configuration (检查配置)
honeyclean info
```

## 🤝 Contributing (贡献)

We welcome contributions! Please feel free to:
- Report bugs (报告错误)
- Suggest features (建议功能)
- Submit pull requests (提交拉取请求)
- Improve documentation (改进文档)

## 📄 License (许可证)

This project is licensed under the MIT License.

## 📞 Support (支持)

For questions and support:
- Create an issue on GitHub
- Check the documentation
- Review example configurations

---

**Happy Data Cleaning! (数据清洗愉快！)** 🍯✨