import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
import os
import json
from typing import Dict, List, Union, Optional, Tuple

class PerformanceTracker:
    """
    A comprehensive performance tracking system that allows users to:
    - Track performance metrics over time
    - Set goals and monitor progress
    - Generate reports and visualizations
    - Export data for further analysis
    """
    
    def __init__(self, name: str, metrics: List[str] = None):
        """
        Initialize a new performance tracker.
        
        Args:
            name: Name of the performance tracking instance
            metrics: List of metrics to track (can be added later)
        """
        self.name = name
        self.metrics = metrics or []
        self.data = pd.DataFrame(columns=['date'] + self.metrics)
        self.goals = {}
        self.notes = {}
        
        # Create directory for saving data if it doesn't exist
        self.data_dir = f"performance_data_{name.lower().replace(' ', '_')}"
        os.makedirs(self.data_dir, exist_ok=True)
        
    def add_metric(self, metric_name: str) -> None:
        """Add a new metric to track."""
        if metric_name not in self.metrics:
            self.metrics.append(metric_name)
            if not metric_name in self.data.columns:
                self.data[metric_name] = np.nan
    
    def remove_metric(self, metric_name: str) -> None:
        """Remove a metric from tracking."""
        if metric_name in self.metrics:
            self.metrics.remove(metric_name)
            if metric_name in self.data.columns:
                self.data = self.data.drop(columns=[metric_name])
    
    def record_data(self, date: Union[str, datetime], values: Dict[str, float], 
                   note: str = None) -> None:
        """
        Record performance data for a specific date.
        
        Args:
            date: Date of the performance data
            values: Dictionary mapping metric names to values
            note: Optional note for this data point
        """
        if isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")
        
        date_str = date.strftime("%Y-%m-%d")
        
        # Add any new metrics found in values
        for metric in values.keys():
            if metric not in self.metrics:
                self.add_metric(metric)
        
        # Check if this date already exists
        if date_str in self.data['date'].values:
            # Update existing row
            for metric, value in values.items():
                self.data.loc[self.data['date'] == date_str, metric] = value
        else:
            # Create new row
            new_row = {'date': date_str}
            for metric in self.metrics:
                new_row[metric] = values.get(metric, np.nan)
            
            self.data = pd.concat([self.data, pd.DataFrame([new_row])], ignore_index=True)
        
        # Sort by date
        self.data['date'] = pd.to_datetime(self.data['date'])
        self.data = self.data.sort_values('date')
        self.data['date'] = self.data['date'].dt.strftime("%Y-%m-%d")
        
        # Add note if provided
        if note:
            self.notes[date_str] = note
    
    def set_goal(self, metric: str, target: float, deadline: Union[str, datetime] = None,
                 description: str = None) -> None:
        """
        Set a performance goal for a specific metric.
        
        Args:
            metric: The metric to set a goal for
            target: Target value to achieve
            deadline: Optional deadline for achieving the goal
            description: Optional description of the goal
        """
        if metric not in self.metrics:
            self.add_metric(metric)
        
        if isinstance(deadline, str):
            deadline = datetime.strptime(deadline, "%Y-%m-%d")
        
        deadline_str = deadline.strftime("%Y-%m-%d") if deadline else None
        
        self.goals[metric] = {
            'target': target,
            'deadline': deadline_str,
            'description': description,
            'created_at': datetime.now().strftime("%Y-%m-%d")
        }
    
    def get_current_value(self, metric: str) -> Optional[float]:
        """Get the most recent value for a specific metric."""
        if not len(self.data) or metric not in self.metrics:
            return None
        
        latest_row = self.data.iloc[-1]
        return latest_row[metric]
    
    def calculate_progress(self, metric: str) -> Optional[Dict]:
        """Calculate progress towards a goal for a specific metric."""
        if metric not in self.goals or metric not in self.metrics or len(self.data) == 0:
            return None
        
        current_value = self.get_current_value(metric)
        if current_value is None or np.isnan(current_value):
            return None
        
        goal = self.goals[metric]
        target = goal['target']
        
        # Find initial value (first non-NaN value)
        mask = ~self.data[metric].isna()
        if not any(mask):
            return None
            
        initial_value = self.data[metric][mask].iloc[0]
        
        # Calculate progress
        total_change_needed = target - initial_value
        current_change = current_value - initial_value
        
        if total_change_needed == 0:
            percentage = 100.0 if current_value >= target else 0.0
        else:
            percentage = (current_change / total_change_needed) * 100
            # Cap at 100% if exceeded
            percentage = min(percentage, 100.0) if total_change_needed > 0 else max(percentage, 100.0)
            
        return {
            'initial': initial_value,
            'current': current_value,
            'target': target,
            'progress_percentage': percentage,
            'remaining': target - current_value
        }
    
    def plot_metric(self, metric: str, show_goal: bool = True, 
                   last_n_days: int = None, ax=None) -> plt.Figure:
        """
        Plot the progress of a specific metric over time.
        
        Args:
            metric: Metric to plot
            show_goal: Whether to show the goal target line
            last_n_days: If provided, show only the last N days
            ax: Optional matplotlib axis to plot on
        
        Returns:
            matplotlib Figure object
        """
        if metric not in self.metrics or len(self.data) == 0:
            raise ValueError(f"No data available for metric: {metric}")
        
        # Create a copy of the data with proper date parsing
        plot_data = self.data.copy()
        plot_data['date'] = pd.to_datetime(plot_data['date'])
        
        # Filter for last n days if specified
        if last_n_days:
            cutoff_date = datetime.now() - timedelta(days=last_n_days)
            plot_data = plot_data[plot_data['date'] >= cutoff_date]
        
        # Filter out NaN values for this metric
        plot_data = plot_data.dropna(subset=[metric])
        
        if len(plot_data) == 0:
            raise ValueError(f"No non-NaN data available for metric: {metric}")
        
        # Create plot
        close_plot = False
        if ax is None:
            fig, ax = plt.subplots(figsize=(10, 6))
            close_plot = True
        
        # Plot the metric data
        ax.plot(plot_data['date'], plot_data[metric], marker='o', linestyle='-', label=metric)
        
        # Add goal line if requested and available
        if show_goal and metric in self.goals:
            target = self.goals[metric]['target']
            ax.axhline(y=target, color='r', linestyle='--', label=f"Goal: {target}")
            
            # Add deadline line if available
            if self.goals[metric]['deadline']:
                deadline = datetime.strptime(self.goals[metric]['deadline'], "%Y-%m-%d")
                if deadline >= min(plot_data['date']) and deadline <= datetime.now() + timedelta(days=30):
                    ax.axvline(x=deadline, color='g', linestyle=':', label=f"Deadline: {self.goals[metric]['deadline']}")
        
        # Add labels and title
        ax.set_xlabel("Date")
        ax.set_ylabel(metric)
        ax.set_title(f"{metric} Over Time")
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # Format x-axis to prevent crowding
        if len(plot_data) > 10:
            plt.xticks(rotation=45)
            ax.xaxis.set_major_locator(plt.MaxNLocator(10))
        
        plt.tight_layout()
        
        if close_plot:
            return fig
        return ax.figure
    
    def plot_dashboard(self, metrics: List[str] = None, last_n_days: int = 30) -> plt.Figure:
        """
        Generate a dashboard with plots for multiple metrics.
        
        Args:
            metrics: List of metrics to include (defaults to all)
            last_n_days: Number of days to show
            
        Returns:
            matplotlib Figure object
        """
        metrics_to_plot = metrics or self.metrics
        metrics_to_plot = [m for m in metrics_to_plot if m in self.metrics]
        
        if not metrics_to_plot:
            raise ValueError("No valid metrics to plot")
        
        # Determine grid size
        n_metrics = len(metrics_to_plot)
        cols = min(3, n_metrics)
        rows = (n_metrics + cols - 1) // cols
        
        fig, axes = plt.subplots(rows, cols, figsize=(5*cols, 4*rows))
        
        # Handle case with only one subplot
        if n_metrics == 1:
            axes = np.array([axes])
        
        # Flatten axes array for easy iteration
        axes = axes.flatten() if hasattr(axes, 'flatten') else [axes]
        
        for i, metric in enumerate(metrics_to_plot):
            try:
                self.plot_metric(metric, show_goal=True, last_n_days=last_n_days, ax=axes[i])
            except ValueError as e:
                axes[i].text(0.5, 0.5, f"No data available for {metric}", 
                           horizontalalignment='center', verticalalignment='center',
                           transform=axes[i].transAxes)
        
        # Hide unused subplots
        for i in range(len(metrics_to_plot), len(axes)):
            axes[i].axis('off')
        
        plt.tight_layout()
        return fig
    
    def generate_report(self) -> Dict:
        """Generate a comprehensive performance report."""
        report = {
            'name': self.name,
            'date_generated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'metrics_count': len(self.metrics),
            'data_points_count': len(self.data),
            'date_range': {
                'start': min(self.data['date']) if len(self.data) else None,
                'end': max(self.data['date']) if len(self.data) else None
            },
            'current_values': {},
            'goals': {},
            'progress': {}
        }
        
        # Add current values for all metrics
        for metric in self.metrics:
            current = self.get_current_value(metric)
            report['current_values'][metric] = None if current is None or np.isnan(current) else current
            
            # Add goal information if available
            if metric in self.goals:
                report['goals'][metric] = self.goals[metric]
                
                # Add progress information
                progress = self.calculate_progress(metric)
                report['progress'][metric] = progress
        
        return report
    
    def save_data(self, filename: str = None) -> str:
        """
        Save the current state to disk.
        
        Args:
            filename: Optional filename, defaults to timestamped name
            
        Returns:
            Path to the saved file
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.name.lower().replace(' ', '_')}_{timestamp}.json"
        
        filepath = os.path.join(self.data_dir, filename)
        
        # Prepare data for serialization
        save_data = {
            'name': self.name,
            'metrics': self.metrics,
            'data': self.data.to_dict(orient='records'),
            'goals': self.goals,
            'notes': self.notes,
            'saved_at': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        with open(filepath, 'w') as f:
            json.dump(save_data, f, indent=2)
            
        return filepath
    
    @classmethod
    def load_data(cls, filepath: str) -> 'PerformanceTracker':
        """
        Load a saved performance tracker from disk.
        
        Args:
            filepath: Path to the saved file
            
        Returns:
            PerformanceTracker instance
        """
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Create a new instance
        tracker = cls(name=data['name'], metrics=data['metrics'])
        
        # Load the data
        tracker.data = pd.DataFrame(data['data'])
        tracker.goals = data['goals']
        tracker.notes = data['notes']
        
        return tracker
    
    def export_to_csv(self, filepath: str = None) -> str:
        """Export data to CSV file."""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.data_dir, f"{self.name.lower().replace(' ', '_')}_{timestamp}.csv")
        
        self.data.to_csv(filepath, index=False)
        return filepath
    
    def export_to_excel(self, filepath: str = None) -> str:
        """Export data to Excel file with formatted dashboard."""
        if filepath is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(self.data_dir, f"{self.name.lower().replace(' ', '_')}_{timestamp}.xlsx")
        
        # Create Excel writer
        with pd.ExcelWriter(filepath, engine='xlsxwriter') as writer:
            # Write data
            self.data.to_excel(writer, sheet_name='Data', index=False)
            
            # Write goals
            goals_df = pd.DataFrame(columns=['Metric', 'Target', 'Deadline', 'Description'])
            for metric, goal in self.goals.items():
                goals_df = pd.concat([goals_df, pd.DataFrame([{
                    'Metric': metric,
                    'Target': goal['target'],
                    'Deadline': goal['deadline'],
                    'Description': goal['description']
                }])], ignore_index=True)
            
            goals_df.to_excel(writer, sheet_name='Goals', index=False)
            
            # Write progress report
            report = self.generate_report()
            progress_data = []
            
            for metric in self.metrics:
                if metric in report['progress'] and report['progress'][metric]:
                    prog = report['progress'][metric]
                    progress_data.append({
                        'Metric': metric,
                        'Initial': prog['initial'],
                        'Current': prog['current'],
                        'Target': prog['target'],
                        'Progress (%)': f"{prog['progress_percentage']:.1f}%",
                        'Remaining': prog['remaining']
                    })
                else:
                    current = report['current_values'].get(metric)
                    progress_data.append({
                        'Metric': metric,
                        'Current': None if current is None else current
                    })
            
            pd.DataFrame(progress_data).to_excel(writer, sheet_name='Progress', index=False)
            
            # Add conditional formatting for progress
            progress_sheet = writer.sheets['Progress']
            progress_sheet.conditional_format('E2:E1000', {
                'type': 'data_bar',
                'bar_color': '#638EC6',
                'min_type': 'num',
                'min_value': 0,
                'max_type': 'num',
                'max_value': 100
            })
        
        return filepath

    def get_stats(self, metric: str) -> Dict:
        """Get statistical information about a metric."""
        if metric not in self.metrics or len(self.data) == 0:
            return None
        
        # Filter out NaN values
        values = self.data[metric].dropna()
        
        if len(values) == 0:
            return None
            
        return {
            'count': len(values),
            'min': values.min(),
            'max': values.max(),
            'mean': values.mean(),
            'median': values.median(),
            'std': values.std(),
            'last_value': values.iloc[-1] if len(values) > 0 else None,
            'trend': 'increasing' if len(values) > 1 and values.iloc[-1] > values.iloc[-2] else
                    'decreasing' if len(values) > 1 and values.iloc[-1] < values.iloc[-2] else 'stable'
        }
    
    def analyze_trends(self, metric: str, window: int = 7) -> Dict:
        """
        Analyze trends for a specific metric.
        
        Args:
            metric: Metric to analyze
            window: Rolling window size for trend calculation
            
        Returns:
            Dictionary with trend analysis
        """
        if metric not in self.metrics or len(self.data) == 0:
            return None
            
        # Create a copy with datetime index
        analysis_data = self.data.copy()
        analysis_data['date'] = pd.to_datetime(analysis_data['date'])
        analysis_data = analysis_data.set_index('date')
        
        # Drop NaN values
        metric_data = analysis_data[metric].dropna()
        
        if len(metric_data) < 2:
            return {'message': 'Not enough data points for trend analysis'}
            
        # Calculate rolling averages
        if len(metric_data) >= window:
            rolling_avg = metric_data.rolling(window=window).mean()
        else:
            rolling_avg = None
            
        # Calculate overall trend (simple linear regression)
        x = np.arange(len(metric_data))
        y = metric_data.values
        
        if len(x) > 1:
            slope, intercept = np.polyfit(x, y, 1)
            
            # Predict values
            trend_line = slope * x + intercept
            
            # Calculate R-squared
            y_mean = np.mean(y)
            ss_tot = np.sum((y - y_mean) ** 2)
            ss_res = np.sum((y - trend_line) ** 2)
            r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0
            
            # Determine trend strength
            if abs(r_squared) < 0.3:
                trend_strength = 'weak'
            elif abs(r_squared) < 0.7:
                trend_strength = 'moderate'
            else:
                trend_strength = 'strong'
                
            # Determine trend direction
            if abs(slope) < 0.001:
                trend_direction = 'stable'
            elif slope > 0:
                trend_direction = 'increasing'
            else:
                trend_direction = 'decreasing'
                
            # Calculate expected value in next period
            next_value = slope * len(metric_data) + intercept
            
            return {
                'trend_direction': trend_direction,
                'trend_strength': trend_strength,
                'slope': slope,
                'r_squared': r_squared,
                'next_value_estimate': next_value,
                'rolling_average': rolling_avg.iloc[-1] if rolling_avg is not None else None,
                'data_points': len(metric_data)
            }
        else:
            return {'message': 'Not enough data points for regression analysis'}

    def compare_periods(self, metric: str, period1: Tuple[str, str], 
                       period2: Tuple[str, str]) -> Dict:
        """
        Compare metric performance between two time periods.
        
        Args:
            metric: Metric to compare
            period1: Tuple of (start_date, end_date) for first period
            period2: Tuple of (start_date, end_date) for second period
            
        Returns:
            Dictionary with comparison results
        """
        if metric not in self.metrics:
            return None
            
        # Parse dates
        p1_start = datetime.strptime(period1[0], "%Y-%m-%d")
        p1_end = datetime.strptime(period1[1], "%Y-%m-%d")
        p2_start = datetime.strptime(period2[0], "%Y-%m-%d")
        p2_end = datetime.strptime(period2[1], "%Y-%m-%d")
        
        # Create a copy with datetime index
        analysis_data = self.data.copy()
        analysis_data['date'] = pd.to_datetime(analysis_data['date'])
        
        # Filter data for each period
        p1_data = analysis_data[(analysis_data['date'] >= p1_start) & 
                              (analysis_data['date'] <= p1_end)][metric].dropna()
        
        p2_data = analysis_data[(analysis_data['date'] >= p2_start) & 
                              (analysis_data['date'] <= p2_end)][metric].dropna()
        
        if len(p1_data) == 0 or len(p2_data) == 0:
            return {'message': 'Insufficient data for one or both periods'}
            
        # Calculate statistics for each period
        p1_stats = {
            'mean': p1_data.mean(),
            'median': p1_data.median(),
            'min': p1_data.min(),
            'max': p1_data.max(),
            'std': p1_data.std(),
            'count': len(p1_data)
        }
        
        p2_stats = {
            'mean': p2_data.mean(),
            'median': p2_data.median(),
            'min': p2_data.min(),
            'max': p2_data.max(),
            'std': p2_data.std(),
            'count': len(p2_data)
        }
        
        # Calculate changes
        mean_change = p2_stats['mean'] - p1_stats['mean']
        mean_change_pct = (mean_change / p1_stats['mean'] * 100) if p1_stats['mean'] != 0 else float('inf')
        
        median_change = p2_stats['median'] - p1_stats['median']
        median_change_pct = (median_change / p1_stats['median'] * 100) if p1_stats['median'] != 0 else float('inf')
        
        return {
            'period1': {
                'start': period1[0],
                'end': period1[1],
                'stats': p1_stats
            },
            'period2': {
                'start': period2[0],
                'end': period2[1],
                'stats': p2_stats
            },
            'comparison': {
                'mean_change': mean_change,
                'mean_change_percentage': mean_change_pct,
                'median_change': median_change,
                'median_change_percentage': median_change_pct,
                'improved': mean_change > 0  # Assumes higher values are better
            }
        }

# Example usage
if __name__ == "__main__":
    # Create a performance tracker for a fitness program
    tracker = PerformanceTracker("Fitness Tracker")
    
    # Add metrics
    tracker.add_metric("weight_kg")
    tracker.add_metric("run_distance_km")
    tracker.add_metric("pushups")
    
    # Set goals
    tracker.set_goal("weight_kg", 75, "2023-12-31", "Target weight by end of year")
    tracker.set_goal("run_distance_km", 10, "2023-11-30", "Be able to run 10K")
    tracker.set_goal("pushups", 50, "2023-10-31", "50 consecutive pushups")
    
    # Record some data
    import random
    
    start_date = datetime(2023, 1, 1)
    weight = 90.0
    run_distance = 3.0
    pushups = 15
    
    for i in range(30):
        date = start_date + timedelta(days=i*3)
        
        # Simulate improvements
        weight = max(weight - random.uniform(0.1, 0.5), 75)
        run_distance = min(run_distance + random.uniform(0.1, 0.3), 10)
        pushups = min(pushups + random.randint(0, 2), 50)
        
        tracker.record_data(
            date,
            {
                "weight_kg": weight,
                "run_distance_km": run_distance,
                "pushups": pushups
            },
            note=f"Day {i+1} of training program"
        )
    
    # Generate a report
    report = tracker.generate_report()
    print(f"Report generated for {report['name']}")
    print(f"Progress on weight goal: {report['progress']['weight_kg']['progress_percentage']:.1f}%")
    
    # Plot a dashboard
    dashboard = tracker.plot_dashboard()
    
    # Save the data
    saved_path = tracker.save_data()
    print(f"Data saved to {saved_path}")
    
    # Export to Excel
    excel_path = tracker.export_to_excel()
    print(f"Excel report saved to {excel_path}")