"""Reporting utilities for the wheat nitrogen content estimator."""

import pandas as pd
from pathlib import Path

def generate_technical_report(df, output_path):
    """
    Generate a technical report with analysis results
    
    Args:
        df (pd.DataFrame): DataFrame with estimation results
        output_path (str or Path): Path to save the report
    """
    output_path = Path(output_path)
    
    with open(output_path, 'w') as f:
        f.write("Above-ground Nitrogen Content Analysis Technical Report\n")
        f.write("================================================\n\n")
        
        # Analysis period
        f.write("1. Analysis Period\n")
        f.write("-----------------\n")
        f.write(f"Start Date: {df['date'].min()}\n")
        f.write(f"End Date: {df['date'].max()}\n")
        f.write(f"Number of Observations: {len(df)}\n\n")
        
        # Overall statistics
        f.write("2. Overall Statistics\n")
        f.write("-------------------\n")
        f.write(f"Mean N Content: {df['n_content'].mean():.2f}% ± {df['rmse'].mean():.2f}%\n")
        f.write(f"Range: {df['n_content'].min():.2f}% - {df['n_content'].max():.2f}%\n")
        f.write(f"Average RMSE: {df['rmse'].mean():.3f}%\n")
        f.write(f"Average R²: {df['r2_mean'].mean():.3f}\n\n")
        
        # Method performance
        f.write("3. Method Performance\n")
        f.write("-------------------\n")
        methods = [col.replace('_estimate', '') 
                  for col in df.columns if col.endswith('_estimate')]
        
        for method in methods:
            f.write(f"\n{method}:\n")
            f.write(f"  - Mean Estimate: {df[f'{method}_estimate'].mean():.2f}%\n")
            f.write(f"  - RMSE: {df[f'{method}_rmse'].mean():.3f}%\n")
            f.write(f"  - R²: {df[f'{method}_r2'].mean():.3f}\n")
            f.write(f"  - Average Weight: {df[f'{method}_weight'].mean():.2f}\n")
        
        # Estimation quality
        f.write("\n4. Estimation Quality Distribution\n")
        f.write("-------------------------------\n")
        quality_dist = df['estimation_quality'].value_counts()
        for quality, count in quality_dist.items():
            percentage = (count / len(df)) * 100
            f.write(f"{quality}: {count} measurements ({percentage:.1f}%)\n")
        
        # References
        f.write("\n5. References\n")
        f.write("------------\n")
        f.write("1. Li et al. (2018). Field Crops Research, 218, 159-174\n")
        f.write("2. Cao et al. (2020). IEEE J-STARS, 13, 2818-2832\n")
        f.write("3. Prey & Schmidhalter (2019). Sensors, 19(21), 4640\n")
        f.write("4. Zheng et al. (2018). Remote Sensing, 10(6), 824\n")

def save_results_csv(df, output_path):
    """
    Save analysis results to CSV
    
    Args:
        df (pd.DataFrame): DataFrame with estimation results
        output_path (str or Path): Path to save the CSV file
    """
    # Ensure all numeric columns are float
    numeric_cols = df.select_dtypes(include=['float', 'int']).columns
    df[numeric_cols] = df[numeric_cols].astype(float)
    
    # Round numeric columns to reasonable precision
    df = df.round({
        'n_content': 2,
        'rmse': 3,
        'r2_mean': 3
    })
    
    # Save to CSV
    df.to_csv(output_path, index=False)

def create_reports(df, output_dir):
    """
    Create all reports
    
    Args:
        df (pd.DataFrame): DataFrame with estimation results
        output_dir (str or Path): Directory to save reports
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    generate_technical_report(df, output_dir / 'technical_report.txt')
    save_results_csv(df, output_dir / 'nitrogen_analysis.csv') 