"""
Setup script for RSI Comparison Tool
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="rsi-comparison-tool",
    version="1.3.0",
    author="RSI Comparison Tool Team",
    author_email="support@rsi-comparison-tool.com",
    description="A comprehensive tool for comparing Regulatory Safety Information (RSI) documents",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/Safety-align",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Healthcare Industry",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.0",
            "flake8>=3.8",
            "mypy>=0.800",
        ],
        "web": [
            "streamlit>=1.29.0",
            "plotly>=5.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "rsi-compare=src.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.txt", "*.md", "*.yml", "*.yaml"],
    },
    keywords="rsi, regulatory, safety, information, comparison, pdf, ocr, healthcare, pharmaceutical",
    project_urls={
        "Bug Reports": "https://github.com/your-username/Safety-align/issues",
        "Source": "https://github.com/your-username/Safety-align",
        "Documentation": "https://github.com/your-username/Safety-align/blob/main/README.md",
    },
)
