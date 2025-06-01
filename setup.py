from setuptools import setup, find_packages

setup(
    name="walter-gis",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "click>=8.1.0",  # CLI framework
        "geopandas>=0.14.0",  # Geospatial data handling
        "shapely>=2.0.0",  # Geometry operations
        "fiona>=1.9.0",  # File format support
        "pyogrio>=0.7.0",  # Fast GIS I/O
        "markdown>=3.5.0",  # Markdown generation
        "gitpython>=3.1.0",  # Git operations
        "requests>=2.31.0",  # API calls
        "rich>=13.7.0",  # Terminal formatting
        "typer>=0.9.0",  # Modern CLI interface
        "python-dotenv>=1.0.0",  # Environment management
        "pyyaml>=6.0.1",  # YAML configuration
        "jinja2>=3.1.0",  # Template rendering
        "streamlit>=1.32.0",  # GUI framework
        "ollama>=0.1.6",  # Ollama Python client
        "plotly>=5.19.0",  # Interactive plots
        "folium>=0.15.1",  # Interactive maps
        "streamlit-folium>=0.18.0",  # Streamlit map integration
        "fpdf>=1.7.2",  # PDF generation
        "openpyxl>=3.1.2",  # Excel support
        "scipy>=1.12.0",  # Scientific computing
        "statsmodels>=0.14.1",  # Statistical analysis
    ],
    extras_require={
        'agol': ["arcgis>=2.2.0"],  # ArcGIS API for Python (optional)
    },
    entry_points={
        "console_scripts": [
            "walter=walter.cli:app",
            "walter-gui=walter.gui:main",
        ],
    },
    author="Brandon Estevez",
    author_email="brandonestevez2007@gmail.com",
    description="Walter - Your AI GIS Assistant for automating geospatial workflows",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/walter",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: GIS",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.9",
) 