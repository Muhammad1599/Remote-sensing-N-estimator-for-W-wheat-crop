import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import rasterio
import os
from pathlib import Path

class SyntheticDataGenerator:
    def __init__(self, output_dir, start_date="2024-02-01", n_timepoints=8):
        """
        Generate synthetic but realistic vegetation indices data for wheat
        
        Args:
            output_dir (str): Directory to save synthetic data
            start_date (str): Start date for time series
            n_timepoints (int): Number of time points to generate
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.start_date = datetime.strptime(start_date, "%Y-%m-%d")
        self.n_timepoints = n_timepoints
        
        # Typical ranges for wheat vegetation indices
        self.index_ranges = {
            'NDVI': (0.3, 0.9),    # Early to peak growth
            'NDRE': (0.2, 0.7),    # Typical range for wheat
            'SAVI': (0.2, 0.8),    # Soil-adjusted VI range
            'GNDVI': (0.3, 0.8),   # Green NDVI range
            'MCARI': (0.1, 0.5),   # Modified Chlorophyll Absorption range
            'CIred-edge': (0.8, 3.5) # Chlorophyll Index range
        }
    
    def generate_growth_curve(self, min_val, max_val, noise_level=0.05):
        """Generate realistic growth curve with some noise"""
        # Generate smooth sigmoid curve
        x = np.linspace(-3, 3, self.n_timepoints)
        base_curve = 1 / (1 + np.exp(-x))
        
        # Scale to desired range
        scaled_curve = min_val + (max_val - min_val) * base_curve
        
        # Add realistic noise
        noise = np.random.normal(0, noise_level, self.n_timepoints)
        noisy_curve = scaled_curve + noise * (max_val - min_val)
        
        # Ensure within bounds
        return np.clip(noisy_curve, min_val, max_val)
    
    def generate_time_series(self):
        """Generate time series data for all indices"""
        dates = [self.start_date + timedelta(days=i*10) for i in range(self.n_timepoints)]
        
        # Generate correlated indices
        data = {}
        for index, (min_val, max_val) in self.index_ranges.items():
            data[index] = self.generate_growth_curve(min_val, max_val)
        
        # Create synthetic images
        for i, date in enumerate(dates):
            self.create_synthetic_image(date, {k: v[i] for k, v in data.items()})
    
    def create_synthetic_image(self, date, indices):
        """Create synthetic multispectral image with given indices"""
        # Image dimensions
        height, width = 100, 100
        
        # Create bands that would give these indices
        # Assuming typical reflectance values for wheat
        nir = np.random.normal(0.45, 0.02, (height, width))  # NIR reflectance
        red = np.random.normal(0.15, 0.02, (height, width))  # Red reflectance
        green = np.random.normal(0.2, 0.02, (height, width)) # Green reflectance
        red_edge = np.random.normal(0.3, 0.02, (height, width)) # Red edge reflectance
        blue = np.random.normal(0.1, 0.02, (height, width))  # Blue reflectance
        
        # Adjust bands to match target indices
        ndvi_target = indices['NDVI']
        nir = red * (1 + ndvi_target)/(1 - ndvi_target)
        
        # Create image file
        filename = self.output_dir / f"synthetic_{date.strftime('%Y%m%d')}.tif"
        
        # Create GeoTIFF
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
            
            # Add metadata
            dst.update_tags(
                date=date.strftime("%Y-%m-%d"),
                description="Synthetic multispectral data for wheat N estimation"
            )

def main():
    """Generate synthetic test data"""
    # Create test data directory
    test_data_dir = Path("test_data/drone_images")
    test_data_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate synthetic time series
    generator = SyntheticDataGenerator(
        output_dir=test_data_dir,
        start_date="2024-02-01",
        n_timepoints=8
    )
    
    print("Generating synthetic time series data...")
    generator.generate_time_series()
    print(f"Created synthetic data in: {test_data_dir}")

if __name__ == "__main__":
    main() 