from setuptools import find_packages, setup

setup(
    name="stock-tech-candlestick",
    version="0.1.0",
    description="A Python project for candlestick pattern analysis with CI/CD workflows",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/your-username/stock-tech-candlestick",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.28.0",
        "numpy>=1.21.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "flake8>=4.0",
            "black>=22.0",
            "mypy>=1.0",
        ],
        "docs": ["sphinx>=4.0", "sphinx-rtd-theme>=1.0"],
        "test": ["pytest>=7.0", "pytest-cov>=4.0"],
    },
    python_requires=">=3.7",
)
