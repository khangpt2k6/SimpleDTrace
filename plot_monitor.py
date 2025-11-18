import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import os
import statistics

CSV_FILE = 'monitor_log.csv'

def load_data():
    """Load monitoring data from CSV file"""
    if not os.path.exists(CSV_FILE):
        print(f"Error: {CSV_FILE} not found!")
        return None
    
    df = pd.read_csv(CSV_FILE)
    
    # Convert timestamp to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Convert success column to boolean if it's string
    if df['success'].dtype == 'object':
        df['success'] = df['success'].astype(str).str.lower() == 'true'
    
    return df

def create_plots(df):
    """Create multiple visualization plots"""
    if df is None or len(df) == 0:
        print("No data to plot!")
        return
    
    # Create figure with subplots
    fig = plt.figure(figsize=(16, 10))
    
    # 1. Time Series Plot - Latency over Time
    ax1 = plt.subplot(2, 2, 1)
    ax1.plot(df['timestamp'], df['latency_ms'], marker='o', markersize=3, linewidth=1, alpha=0.7)
    ax1.set_xlabel('Time', fontsize=10)
    ax1.set_ylabel('Latency (ms)', fontsize=10)
    ax1.set_title('Latency Over Time', fontsize=12, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Add average line
    avg_latency = df['latency_ms'].mean()
    ax1.axhline(y=avg_latency, color='r', linestyle='--', linewidth=2, label=f'Average: {avg_latency:.2f} ms')
    ax1.legend()
    
    # 2. Histogram - Latency Distribution
    ax2 = plt.subplot(2, 2, 2)
    ax2.hist(df['latency_ms'], bins=30, edgecolor='black', alpha=0.7, color='skyblue')
    ax2.set_xlabel('Latency (ms)', fontsize=10)
    ax2.set_ylabel('Frequency', fontsize=10)
    ax2.set_title('Latency Distribution', fontsize=12, fontweight='bold')
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Add statistics lines
    mean_latency = df['latency_ms'].mean()
    median_latency = df['latency_ms'].median()
    ax2.axvline(x=mean_latency, color='r', linestyle='--', linewidth=2, label=f'Mean: {mean_latency:.2f} ms')
    ax2.axvline(x=median_latency, color='g', linestyle='--', linewidth=2, label=f'Median: {median_latency:.2f} ms')
    ax2.legend()
    
    # 3. Success Rate Visualization
    ax3 = plt.subplot(2, 2, 3)
    success_count = df['success'].sum()
    total_count = len(df)
    failure_count = total_count - success_count
    success_rate = (success_count / total_count * 100) if total_count > 0 else 0
    
    colors = ['#2ecc71', '#e74c3c']
    labels = [f'Success ({success_count})', f'Failure ({failure_count})']
    sizes = [success_count, failure_count]
    
    # Only plot if there are failures, otherwise just show success
    if failure_count > 0:
        ax3.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, colors=colors)
    else:
        ax3.pie([success_count], labels=[f'Success ({success_count})'], autopct='%1.1f%%', 
                startangle=90, colors=[colors[0]])
    
    ax3.set_title(f'Success Rate: {success_rate:.2f}%', fontsize=12, fontweight='bold')
    
    # 4. Statistics Summary Table
    ax4 = plt.subplot(2, 2, 4)
    ax4.axis('off')
    
    # Calculate statistics
    stats_data = {
        'Metric': [
            'Total Requests',
            'Success Rate',
            'Average Latency',
            'Median Latency',
            'Min Latency',
            'Max Latency',
            'Std Deviation',
            'P95 Latency',
            'P99 Latency'
        ],
        'Value': [
            f"{total_count}",
            f"{success_rate:.2f}%",
            f"{df['latency_ms'].mean():.2f} ms",
            f"{df['latency_ms'].median():.2f} ms",
            f"{df['latency_ms'].min():.2f} ms",
            f"{df['latency_ms'].max():.2f} ms",
            f"{df['latency_ms'].std():.2f} ms",
            f"{df['latency_ms'].quantile(0.95):.2f} ms",
            f"{df['latency_ms'].quantile(0.99):.2f} ms"
        ]
    }
    
    table = ax4.table(cellText=list(zip(stats_data['Metric'], stats_data['Value'])),
                     colLabels=['Metric', 'Value'],
                     cellLoc='left',
                     loc='center',
                     colWidths=[0.5, 0.5])
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1, 2)
    
    # Style the header
    for i in range(2):
        table[(0, i)].set_facecolor('#3498db')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    ax4.set_title('Statistics Summary', fontsize=12, fontweight='bold', pad=20)
    
    # Adjust layout
    plt.tight_layout()
    
    # Save the plot
    output_file = 'monitor_plots.png'
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Plots saved to: {output_file}")
    
    # Display the plot
    plt.show()
    
    # Print summary to console
    print("\n" + "="*50)
    print("MONITORING DATA SUMMARY")
    print("="*50)
    print(f"Total Requests: {total_count}")
    print(f"Success Rate: {success_rate:.2f}%")
    print(f"Average Latency: {df['latency_ms'].mean():.2f} ms")
    print(f"Median Latency: {df['latency_ms'].median():.2f} ms")
    print(f"Min Latency: {df['latency_ms'].min():.2f} ms")
    print(f"Max Latency: {df['latency_ms'].max():.2f} ms")
    print(f"Std Deviation: {df['latency_ms'].std():.2f} ms")
    print(f"95th Percentile: {df['latency_ms'].quantile(0.95):.2f} ms")
    print(f"99th Percentile: {df['latency_ms'].quantile(0.99):.2f} ms")
    print("="*50)

def main():
    print(f"Loading data from {CSV_FILE}...")
    df = load_data()
    
    if df is not None:
        print(f"✓ Loaded {len(df)} data points")
        print("Generating plots...")
        create_plots(df)
    else:
        print("Failed to load data. Please ensure monitor.py has been run first.")

if __name__ == '__main__':
    main()

