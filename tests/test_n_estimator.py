"""Tests for the nitrogen content estimator."""

import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from wheat_n_estimation import NitrogenEstimator

@pytest.fixture
def sample_indices():
    """Sample vegetation indices for testing"""
    return {
        'NDVI': 0.7,
        'NDRE': 0.5,
        'SAVI': 0.6,
        'GNDVI': 0.65,
        'MCARI': 0.3,
        'CIred-edge': 2.0
    }

@pytest.fixture
def time_series_indices():
    """Sample time series data for testing"""
    dates = [datetime(2024, 2, 1) + timedelta(days=i*10) for i in range(8)]
    
    indices = []
    for date in dates:
        # Create slightly varying indices
        base_indices = {
            'NDVI': 0.7 + np.random.normal(0, 0.05),
            'NDRE': 0.5 + np.random.normal(0, 0.05),
            'SAVI': 0.6 + np.random.normal(0, 0.05),
            'GNDVI': 0.65 + np.random.normal(0, 0.05),
            'MCARI': 0.3 + np.random.normal(0, 0.05),
            'CIred-edge': 2.0 + np.random.normal(0, 0.2)
        }
        indices.append({
            'date': date,
            'indices': base_indices
        })
    
    return indices

def test_n_estimator_initialization():
    """Test NitrogenEstimator initialization"""
    estimator = NitrogenEstimator()
    assert estimator is not None

def test_single_estimation(sample_indices):
    """Test estimation from single set of indices"""
    estimator = NitrogenEstimator()
    result = estimator.estimate_n_content_from_indices(sample_indices)
    
    assert isinstance(result, dict)
    assert 'n_content' in result
    assert 'confidence_intervals' in result
    assert 'uncertainty' in result
    assert 'method_weights' in result
    
    # Check N content is within physiological limits
    assert 1.5 <= result['n_content'] <= 6.0
    
    # Check uncertainty metrics
    assert 0 <= result['uncertainty']['rmse'] <= 1.0
    assert 0 <= result['uncertainty']['r2_mean'] <= 1.0

def test_time_series_prediction(time_series_indices):
    """Test prediction on time series data"""
    estimator = NitrogenEstimator()
    predictions = estimator.predict(time_series_indices)
    
    assert len(predictions) == len(time_series_indices)
    
    for pred in predictions:
        assert isinstance(pred, dict)
        assert 'date' in pred
        assert 'n_content' in pred
        assert 'uncertainty' in pred
        
        # Check N content is within physiological limits
        assert 1.5 <= pred['n_content'] <= 6.0
        
        # Check uncertainty metrics
        assert 0 <= pred['uncertainty']['rmse'] <= 1.0
        assert 0 <= pred['uncertainty']['r2_mean'] <= 1.0

def test_estimation_quality():
    """Test estimation quality assessment"""
    estimator = NitrogenEstimator()
    
    # Test high confidence case
    high_conf = {'r2_mean': 0.9, 'rmse': 0.3}
    assert estimator.get_estimation_quality(high_conf) == "High Confidence"
    
    # Test moderate confidence case
    mod_conf = {'r2_mean': 0.8, 'rmse': 0.4}
    assert estimator.get_estimation_quality(mod_conf) == "Moderate Confidence"
    
    # Test low confidence case
    low_conf = {'r2_mean': 0.7, 'rmse': 0.5}
    assert estimator.get_estimation_quality(low_conf) == "Low Confidence"

def test_invalid_indices():
    """Test handling of invalid indices"""
    estimator = NitrogenEstimator()
    
    with pytest.raises(ValueError):
        estimator.estimate_n_content_from_indices({})
    
    with pytest.raises(ValueError):
        estimator.estimate_n_content_from_indices({'NDVI': -1.0})  # Invalid NDVI 