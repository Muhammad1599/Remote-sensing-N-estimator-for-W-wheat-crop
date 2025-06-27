"""Tests for the data loader module."""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import rasterio
from datetime import datetime
from wheat_n_estimation import DataLoader

@pytest.fixture
def sample_image_dir(tmp_path):
    """Create sample image directory with synthetic data"""
    img_dir = tmp_path / "test_images"
    img_dir.mkdir()
    
    # Create sample images
    dates = [datetime(2024, 2, 1), datetime(2024, 2, 10)]
    height, width = 10, 10
    
    for date in dates:
        filename = img_dir / f"synthetic_{date.strftime('%Y%m%d')}.tif"
        
        # Create synthetic bands
        blue = np.random.normal(0.1, 0.02, (height, width))
        green = np.random.normal(0.2, 0.02, (height, width))
        red = np.random.normal(0.15, 0.02, (height, width))
        nir = np.random.normal(0.45, 0.02, (height, width))
        red_edge = np.random.normal(0.3, 0.02, (height, width))
        
        # Save as GeoTIFF
        transform = rasterio.transform.from_origin(0, 0, 1, 1)
        with rasterio.open(
            filename,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=5,
            dtype=np.float32,
            crs='+proj=utm +zone=32 +datum=WGS84 +units=m +no_defs',
            transform=transform
        ) as dst:
            dst.write(blue, 1)
            dst.write(green, 2)
            dst.write(red, 3)
            dst.write(nir, 4)
            dst.write(red_edge, 5)
            
            dst.update_tags(
                date=date.strftime("%Y-%m-%d"),
                description="Test data"
            )
    
    return img_dir

def test_data_loader_initialization(sample_image_dir):
    """Test DataLoader initialization"""
    loader = DataLoader(sample_image_dir)
    assert loader is not None
    assert loader.data_dir == Path(sample_image_dir)

def test_load_time_series(sample_image_dir):
    """Test loading time series data"""
    loader = DataLoader(sample_image_dir)
    df = loader.load_time_series()
    
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2  # Two test images
    
    # Check required columns
    required_cols = ['date', 'blue', 'green', 'red', 'nir', 'red_edge']
    assert all(col in df.columns for col in required_cols)
    
    # Check data types
    assert pd.api.types.is_datetime64_any_dtype(df['date'])
    assert all(pd.api.types.is_float_dtype(df[col]) for col in required_cols[1:])
    
    # Check value ranges
    for band in ['blue', 'green', 'red', 'nir', 'red_edge']:
        assert df[band].between(0, 1).all()

def test_calculate_vegetation_indices(sample_image_dir):
    """Test vegetation indices calculation"""
    loader = DataLoader(sample_image_dir)
    indices = loader.calculate_vegetation_indices()
    
    assert isinstance(indices, list)
    assert len(indices) == 2  # Two test images
    
    for entry in indices:
        assert isinstance(entry, dict)
        assert 'date' in entry
        assert 'indices' in entry
        
        # Check all required indices are present
        required_indices = ['NDVI', 'NDRE', 'SAVI', 'GNDVI', 'MCARI', 'CIred-edge']
        assert all(idx in entry['indices'] for idx in required_indices)
        
        # Check index ranges
        assert -1 <= entry['indices']['NDVI'] <= 1
        assert -1 <= entry['indices']['NDRE'] <= 1
        assert -1.5 <= entry['indices']['SAVI'] <= 1.5
        assert -1 <= entry['indices']['GNDVI'] <= 1
        assert entry['indices']['MCARI'] >= 0
        assert entry['indices']['CIred-edge'] >= -1

def test_invalid_data_dir():
    """Test handling of invalid data directory"""
    with pytest.raises(ValueError):
        loader = DataLoader("nonexistent_dir")
        loader.load_time_series()

def test_empty_data_dir(tmp_path):
    """Test handling of empty data directory"""
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()
    
    with pytest.raises(ValueError):
        loader = DataLoader(empty_dir)
        loader.load_time_series() 