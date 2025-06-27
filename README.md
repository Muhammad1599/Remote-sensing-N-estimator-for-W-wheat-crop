# Wheat Nitrogen Content Estimator

A Python-based pipeline for estimating above-ground nitrogen content in winter wheat using drone-based vegetation indices.

## Features

- Processes multi-spectral drone imagery to calculate vegetation indices
- Implements scientifically validated N estimation methods from peer-reviewed literature
- Supports multiple vegetation indices: NDVI, NDRE, SAVI, GNDVI, MCARI, CIred-edge
- Provides uncertainty quantification and quality metrics
- Generates comprehensive analysis reports and visualizations

## Scientific Background

The estimation methods are based on peer-reviewed research:

1. Li et al. (2018): NDRE-based estimation (R² = 0.89)
2. Cao et al. (2020): CIred-edge based estimation (R² = 0.87)
3. Prey & Schmidhalter (2019): MCARI-based estimation (R² = 0.83)
4. Zheng et al. (2018): SAVI correction

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/wheat-n-estimator.git
cd wheat-n-estimator

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python wheat_n_estimation/pipeline.py --data_dir path/to/drone/images --output_dir path/to/output
```

### Input Data Requirements

The pipeline expects multi-spectral drone imagery with the following bands:
1. Blue
2. Green
3. Red
4. NIR (Near-Infrared)
5. Red Edge

Images should be in GeoTIFF format with proper metadata including acquisition date.

### Output

The pipeline generates:
1. Time series of N content estimates
2. Uncertainty metrics (RMSE, R²)
3. Method comparison plots
4. Technical report with statistical analysis
5. CSV file with detailed results

## Project Structure

```
wheat-n-estimator/
├── wheat_n_estimation/       # Main package
│   ├── __init__.py
│   ├── pipeline.py          # Main pipeline
│   ├── data_loader.py       # Data loading utilities
│   ├── n_estimator.py       # N estimation algorithms
│   └── utils/               # Utility functions
├── tests/                   # Test suite
├── docs/                    # Documentation
├── examples/                # Example notebooks
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use this tool in your research, please cite:

```bibtex
@misc{wheat-n-estimator,
  author = {Your Name},
  title = {Wheat Nitrogen Content Estimator},
  year = {2024},
  publisher = {GitHub},
  url = {https://github.com/yourusername/wheat-n-estimator}
}
```

## References

1. Li, F., et al. (2018). "Improving estimation of summer wheat nitrogen status using red edge-based spectral vegetation indices." Field Crops Research, 218, 159-174.
2. Cao, Q., et al. (2020). "Estimating winter wheat above-ground nitrogen content using multispectral vegetation indices from UAV-based imagery." IEEE Journal of Selected Topics in Applied Earth Observations and Remote Sensing, 13, 2818-2832.
3. Prey, L., & Schmidhalter, U. (2019). "Temporal and Spectral Optimization of Vegetation Indices for Estimating Grain Nitrogen Uptake and Late-Seasonal Nitrogen Traits in Wheat." Sensors, 19(21), 4640.
4. Zheng, H., et al. (2018). "Evaluation of RGB, Color-Infrared and Multispectral Images Acquired from Unmanned Aerial Systems for the Estimation of Nitrogen Accumulation in Rice." Remote Sensing, 10(6), 824. 