"""
Walter - Your AI GIS Assistant
"""

__version__ = "0.1.0"
__author__ = "Brandon Estevez"
__email__ = "your.email@example.com"

from .cli import app
from . import commands

__all__ = ["app", "commands"] 