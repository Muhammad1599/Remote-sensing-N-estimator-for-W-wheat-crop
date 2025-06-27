"""Visualization utilities for the wheat nitrogen content estimator."""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from pathlib import Path

def plot_time_series(df, output_path, title="Nitrogen Content Time Series"):
    """
    Create time series plot with uncertainty bands
    
    Args:
        df (pd.DataFrame): DataFrame with date, n_content, and rmse columns
        output_path (str or Path): Path to save the plot
        title (str): Plot title
    """
    plt.figure(figsize=(12, 8))
    
    # Ensure date is datetime
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])
    
    # Sort by date
    df = df.sort_values('date')
    
    # Plot N content with uncertainty bands
    plt.fill_between(df['date'], 
                    df['n_content'] - df['rmse'],
                    df['n_content'] + df['rmse'],
                    alpha=0.2, label='±RMSE')
    
    plt.plot(df['date'], df['n_content'], 'b-', 
            label='N Content', linewidth=2)
    
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('N Content (%)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_method_comparison(df, output_path):
    """
    Create comparison plot of different estimation methods
    
    Args:
        df (pd.DataFrame): DataFrame with estimation results
        output_path (str or Path): Path to save the plot
    """
    plt.figure(figsize=(10, 6))
    
    methods = [col.replace('_estimate', '') 
              for col in df.columns if col.endswith('_estimate')]
    
    for method in methods:
        plt.scatter(df['n_content'], df[f'{method}_estimate'],
                  label=f'{method} (R² = {df[f"{method}_r2"].mean():.2f})')
    
    plt.plot([df['n_content'].min(), df['n_content'].max()],
            [df['n_content'].min(), df['n_content'].max()],
            'k--', label='1:1 Line')
    
    plt.xlabel('Ensemble N Content Estimate (%)')
    plt.ylabel('Individual Method Estimates (%)')
    plt.title('Comparison of Estimation Methods')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def plot_uncertainty_analysis(df, output_path):
    """
    Create uncertainty analysis plots
    
    Args:
        df (pd.DataFrame): DataFrame with uncertainty metrics
        output_path (str or Path): Path to save the plot
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
    
    # Plot 1: RMSE distribution
    rmse_cols = [col for col in df.columns if col.endswith('_rmse')]
    sns.boxplot(data=df[rmse_cols], ax=ax1)
    ax1.set_title('RMSE Distribution by Method')
    ax1.set_xticklabels([col.replace('_rmse', '') for col in rmse_cols], 
                        rotation=45)
    ax1.set_ylabel('RMSE (%)')
    
    # Plot 2: R² distribution
    r2_cols = [col for col in df.columns if col.endswith('_r2')]
    sns.boxplot(data=df[r2_cols], ax=ax2)
    ax2.set_title('R² Distribution by Method')
    ax2.set_xticklabels([col.replace('_r2', '') for col in r2_cols], 
                        rotation=45)
    ax2.set_ylabel('R²')
    
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()

def create_report_plots(df, output_dir):
    """
    Create all report plots
    
    Args:
        df (pd.DataFrame): DataFrame with estimation results
        output_dir (str or Path): Directory to save plots
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    plot_time_series(df, output_dir / 'n_content_analysis.png')
    plot_method_comparison(df, output_dir / 'method_comparison.png')
    plot_uncertainty_analysis(df, output_dir / 'uncertainty_analysis.png') 