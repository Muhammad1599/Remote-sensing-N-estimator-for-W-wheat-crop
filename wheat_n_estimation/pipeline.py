from pathlib import Path
import numpy as np
import pandas as pd
from data_loader import DataLoader
from n_estimator import NitrogenEstimator
import matplotlib.pyplot as plt
import seaborn as sns

class NitrogenEstimationPipeline:
    def __init__(self, data_dir, output_dir):
        """
        Initialize the pipeline
        
        Args:
            data_dir (str): Directory containing drone imagery data
            output_dir (str): Directory for saving outputs
        """
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.data_loader = DataLoader(data_dir)
        self.n_estimator = NitrogenEstimator()
        
    def run_pipeline(self):
        """Run the nitrogen content estimation pipeline"""
        # 1. Load and process time series data
        print("Loading time series data...")
        time_series_data = self.data_loader.load_time_series()
        
        # 2. Calculate vegetation indices
        print("Calculating vegetation indices...")
        indices = self.data_loader.calculate_vegetation_indices()
        
        # 3. Estimate nitrogen content
        print("Estimating above-ground nitrogen content...")
        analysis_results = self.n_estimator.predict(indices)
        
        # 4. Save results and generate visualizations
        self._save_results(analysis_results, indices)
        
        return analysis_results
    
    def _save_results(self, analysis_results, indices):
        """Save analysis results and generate visualizations"""
        # Create results dataframe
        results = []
        for analysis in analysis_results:
            result = {
                'date': analysis['date'],
                'n_content': analysis['n_content'],
                'rmse': analysis['uncertainty']['rmse'],
                'r2_mean': analysis['uncertainty']['r2_mean'],
                'estimation_quality': self.n_estimator.get_estimation_quality(analysis['uncertainty'])
            }
            
            # Add method weights
            for method, weight in analysis['method_weights'].items():
                result[f'{method}_weight'] = weight
            
            # Add individual estimates and their metrics
            for method, ci in analysis['confidence_intervals'].items():
                result[f'{method}_estimate'] = ci['estimate']
                result[f'{method}_rmse'] = ci['rmse']
                result[f'{method}_r2'] = ci['r2']
            
            results.append(result)
        
        results_df = pd.DataFrame(results)
        
        # Save detailed results
        results_df.to_csv(self.output_dir / 'nitrogen_analysis.csv', index=False)
        
        # Generate visualizations
        self._plot_time_series_analysis(results_df)
        self._plot_method_comparison(results_df)
        self._plot_uncertainty_analysis(results_df)
        
        # Save technical report
        self._save_technical_report(results_df)
    
    def _plot_time_series_analysis(self, df):
        """Create time series plots with uncertainty bands"""
        plt.figure(figsize=(12, 8))
        
        # Convert date to datetime if it's not already
        if not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df['date'])
        
        # Sort by date
        df = df.sort_values('date')
        
        # Plot N content with uncertainty bands
        plt.fill_between(df['date'], 
                        df['n_content'] - df['rmse'],
                        df['n_content'] + df['rmse'],
                        alpha=0.2, label='±RMSE')
        
        plt.plot(df['date'], df['n_content'], 'b-', label='N Content', linewidth=2)
        
        # Add individual method estimates
        methods = [col.replace('_estimate', '') 
                  for col in df.columns if col.endswith('_estimate')]
        
        for method in methods:
            plt.plot(df['date'], df[f'{method}_estimate'], '--', 
                    label=f'{method} Estimate', alpha=0.6)
        
        plt.title('Above-ground Nitrogen Content Estimation with Uncertainty')
        plt.xlabel('Date')
        plt.ylabel('N Content (%)')
        plt.legend()
        plt.grid(True)
        plt.xticks(rotation=45)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'n_content_analysis.png')
        plt.close()
    
    def _plot_method_comparison(self, df):
        """Create comparison plot of different estimation methods"""
        methods = [col.replace('_estimate', '') 
                  for col in df.columns if col.endswith('_estimate')]
        
        plt.figure(figsize=(10, 6))
        
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
        plt.savefig(self.output_dir / 'method_comparison.png')
        plt.close()
    
    def _plot_uncertainty_analysis(self, df):
        """Create uncertainty analysis plots"""
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
        
        # Plot 1: RMSE distribution
        sns.boxplot(data=df[[col for col in df.columns if col.endswith('_rmse')]],
                   ax=ax1)
        ax1.set_title('RMSE Distribution by Method')
        ax1.set_xticklabels(ax1.get_xticklabels(), rotation=45)
        
        # Plot 2: R² distribution
        sns.boxplot(data=df[[col for col in df.columns if col.endswith('_r2')]],
                   ax=ax2)
        ax2.set_title('R² Distribution by Method')
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
        
        plt.tight_layout()
        plt.savefig(self.output_dir / 'uncertainty_analysis.png')
        plt.close()
    
    def _save_technical_report(self, df):
        """Generate and save technical report with statistical analysis"""
        with open(self.output_dir / 'technical_report.txt', 'w') as f:
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

def main():
    """Main function to run the pipeline"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Estimate above-ground nitrogen content using vegetation indices')
    parser.add_argument('--data_dir', required=True,
                      help='Directory containing drone imagery')
    parser.add_argument('--output_dir', required=True,
                      help='Directory for outputs')
    
    args = parser.parse_args()
    
    pipeline = NitrogenEstimationPipeline(args.data_dir, args.output_dir)
    results = pipeline.run_pipeline()
    
    print("\nAnalysis completed successfully!")
    print("\nLatest Estimation:")
    latest = results[-1]
    print(f"Date: {latest['date']}")
    print(f"N Content: {latest['n_content']:.2f}% ± {latest['uncertainty']['rmse']:.2f}%")
    print(f"Estimation Quality: {pipeline.n_estimator.get_estimation_quality(latest['uncertainty'])}")
    print(f"Average R²: {latest['uncertainty']['r2_mean']:.3f}")

if __name__ == "__main__":
    main() 