"""
Setup script for HoneyClean package.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="honeyclean",
    version="1.0.0",
    author="HoneyClean Team",
    author_email="info@honeyclean.com",
    description="Automated data profiling and cleaning recommendations with PowerPoint generation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/honeyclean/honeyclean",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.6.0",
        "seaborn>=0.12.0",
        "plotly>=5.14.0",
        "scipy>=1.10.0",
        "scikit-learn>=1.3.0",
        "click>=8.0.0",
        "python-pptx>=0.6.21",
        "missingno>=0.5.2",
        "pillow>=9.0.0",
        "python-dateutil>=2.8.0",
        "tomli>=2.0.0; python_version<'3.11'",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "jupyter": [
            "ipykernel>=6.20.0",
            "jupyter>=1.0.0",
            "notebook>=6.5.0",
            "jupyterlab>=3.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "honeyclean=honeyclean.cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "honeyclean": ["*.toml", "templates/*"],
    },
)