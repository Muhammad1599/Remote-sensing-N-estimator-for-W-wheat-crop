"""
Wheat Nitrogen Content Estimator

A Python package for estimating above-ground nitrogen content in winter wheat
using drone-based vegetation indices.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__email__ = "your.email@example.com"

from .data_loader import DataLoader
from .n_estimator import NitrogenEstimator
from .pipeline import NitrogenEstimationPipeline

__all__ = ['DataLoader', 'NitrogenEstimator', 'NitrogenEstimationPipeline'] 