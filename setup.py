"""
Setup configuration for Garmin Workout Creator
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="garmin-workout-creator",
    version="0.1.0",
    description="Create Garmin workouts from natural language descriptions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Ofir Talmor",
    python_requires=">=3.8",
    packages=find_packages(),
    py_modules=["cli"],  # Include cli.py as a standalone module
    install_requires=[
        "anthropic>=0.18.0",
        "google-genai>=1.0.0",
        "pydantic>=2.0.0",
        "garth>=0.4.0",
        "typer>=0.9.0",
        "python-dotenv>=1.0.0",
        "rich>=13.0.0",
    ],
    entry_points={
        "console_scripts": [
            "garmin-workout=cli:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
