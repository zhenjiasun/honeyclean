# HoneyClean

**Automated Data Profiling and Cleaning Package**

HoneyClean is a comprehensive Python package for automated data profiling, cleaning recommendations, and professional PowerPoint report generation. It provides intelligent analysis of datasets with actionable insights for data scientists and analysts.

## Features

- 🔍 **Comprehensive Data Analysis**: Automatic detection and analysis of numeric, categorical, datetime, and text data
- 📊 **Professional Visualizations**: High-quality plots optimized for presentations
- 📋 **Intelligent Recommendations**: Data type-specific cleaning suggestions
- 📑 **PowerPoint Generation**: Automated creation of professional presentation reports
- ⚙️ **Configurable**: TOML-based configuration with flexible settings
- 🖥️ **CLI Interface**: Easy-to-use command-line tools
- 📓 **Jupyter Support**: Seamless integration with Jupyter notebooks

## Installation

### Using Conda (Recommended)

```bash
# Clone the repository
git clone https://github.com/honeyclean/honeyclean.git
cd honeyclean

# Create and activate conda environment
conda env create -f environment.yml
conda activate honeyclean

# Install package in development mode
pip install -e .