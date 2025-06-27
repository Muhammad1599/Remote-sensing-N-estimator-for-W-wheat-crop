import pandas as pd
import numpy as np
from pathlib import Path
import rasterio
from datetime import datetime

class DataLoader:
    def __init__(self, data_dir):
        """Initialize data loader
        
        Args:
            data_dir (str): Directory containing drone imagery data
        """
        self.data_dir = Path(data_dir)
        
    def load_time_series(self):
        """Load time series data from drone imagery"""
        # Get all tiff files
        image_files = sorted(self.data_dir.glob('*.tif'))
        
        if not image_files:
            raise ValueError(f"No .tif files found in {self.data_dir}")
        
        time_series = []
        for img_file in image_files:
            with rasterio.open(img_file) as src:
                # Read metadata
                date_str = src.tags().get('date')
                if date_str:
                    date = datetime.strptime(date_str, "%Y-%m-%d")
                else:
                    # Try to parse from filename
                    date_str = img_file.stem.split('_')[-1]
                    date = datetime.strptime(date_str, "%Y%m%d")
                
                # Read bands
                blue = src.read(1)
                green = src.read(2)
                red = src.read(3)
                nir = src.read(4)
                red_edge = src.read(5)
                
                # Take mean values (assuming homogeneous field)
                time_series.append({
                    'date': date,
                    'blue': float(np.mean(blue)),
                    'green': float(np.mean(green)),
                    'red': float(np.mean(red)),
                    'nir': float(np.mean(nir)),
                    'red_edge': float(np.mean(red_edge))
                })
        
        return pd.DataFrame(time_series)
    
    def calculate_vegetation_indices(self):
        """Calculate vegetation indices from drone imagery"""
        df = self.load_time_series()
        time_series_indices = []
        
        for _, row in df.iterrows():
            # Calculate indices
            indices = {
                'NDVI': (row['nir'] - row['red']) / (row['nir'] + row['red']),
                'NDRE': (row['nir'] - row['red_edge']) / (row['nir'] + row['red_edge']),
                'SAVI': 1.5 * (row['nir'] - row['red']) / (row['nir'] + row['red'] + 0.5),
                'GNDVI': (row['nir'] - row['green']) / (row['nir'] + row['green']),
                'MCARI': ((row['red_edge'] - row['red']) - 0.2 * (row['red_edge'] - row['green'])) * (row['red_edge'] / row['red']),
                'CIred-edge': (row['nir'] / row['red_edge']) - 1
            }
            
            time_series_indices.append({
                'date': row['date'],
                'indices': indices
            })
        
        return time_series_indices 