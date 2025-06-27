"""Tests for the nitrogen estimation pipeline."""

import pytest
import numpy as np
import pandas as pd
from pathlib import Path
import shutil
from datetime import datetime
import rasterio
from wheat_n_estimation import NitrogenEstimationPipeline

@pytest.fixture
def sample_data_dir(tmp_path):
    """Create sample data directory with synthetic images"""
    data_dir = tmp_path / "test_data"
    data_dir.mkdir()
    
    # Create sample images
    dates = [datetime(2024, 2, 1), datetime(2024, 2, 10)]
    height, width = 10, 10
    
    for date in dates:
        filename = data_dir / f"synthetic_{date.strftime('%Y%m%d')}.tif"
        
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
    
    return data_dir

@pytest.fixture
def output_dir(tmp_path):
    """Create output directory"""
    output_dir = tmp_path / "test_output"
    output_dir.mkdir()
    return output_dir

def test_pipeline_initialization(sample_data_dir, output_dir):
    """Test pipeline initialization"""
    pipeline = NitrogenEstimationPipeline(sample_data_dir, output_dir)
    assert pipeline is not None
    assert pipeline.data_dir == Path(sample_data_dir)
    assert pipeline.output_dir == Path(output_dir)

def test_pipeline_run(sample_data_dir, output_dir):
    """Test running the complete pipeline"""
    pipeline = NitrogenEstimationPipeline(sample_data_dir, output_dir)
    results = pipeline.run_pipeline()
    
    assert results is not None
    assert len(results) == 2  # Two test images
    
    # Check output files
    assert (output_dir / 'nitrogen_analysis.csv').exists()
    assert (output_dir / 'technical_report.txt').exists()
    assert (output_dir / 'n_content_analysis.png').exists()
    assert (output_dir / 'method_comparison.png').exists()
    assert (output_dir / 'uncertainty_analysis.png').exists()
    
    # Check results structure
    for result in results:
        assert isinstance(result, dict)
        assert 'date' in result
        assert 'n_content' in result
        assert 'uncertainty' in result
        assert 'confidence_intervals' in result
        assert 'method_weights' in result
        
        # Check value ranges
        assert 1.5 <= result['n_content'] <= 6.0
        assert 0 <= result['uncertainty']['rmse'] <= 1.0
        assert 0 <= result['uncertainty']['r2_mean'] <= 1.0

def test_pipeline_with_invalid_data_dir(output_dir):
    """Test pipeline with invalid data directory"""
    with pytest.raises(ValueError):
        pipeline = NitrogenEstimationPipeline("nonexistent_dir", output_dir)
        pipeline.run_pipeline()

def test_pipeline_with_invalid_output_dir(sample_data_dir):
    """Test pipeline with invalid output directory"""
    # Create a file instead of a directory
    invalid_dir = sample_data_dir / "not_a_dir"
    invalid_dir.touch()
    
    with pytest.raises(ValueError):
        pipeline = NitrogenEstimationPipeline(sample_data_dir, invalid_dir)
        pipeline.run_pipeline()

def test_pipeline_results_consistency(sample_data_dir, output_dir):
    """Test consistency of pipeline results"""
    pipeline = NitrogenEstimationPipeline(sample_data_dir, output_dir)
    results = pipeline.run_pipeline()
    
    # Load CSV results
    df = pd.read_csv(output_dir / 'nitrogen_analysis.csv')
    
    assert len(df) == len(results)
    
    # Check if CSV results match pipeline results
    for i, result in enumerate(results):
        assert abs(df.iloc[i]['n_content'] - result['n_content']) < 1e-6
        assert abs(df.iloc[i]['rmse'] - result['uncertainty']['rmse']) < 1e-6 