import pandas as pd
import matplotlib.pyplot as plt
import os

# --- Configuration ---
LOG_FILE = os.path.join(os.path.dirname(__file__), 'results', 'performance_log.txt')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'results')

def parse_log_file(log_path):
    """Parses the performance log file and returns a pandas DataFrame."""
    records = []
    with open(log_path, 'r') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            
            try:
                parts = {p.split(':')[0].strip(): p.split(':')[1].strip() for p in line.split(',')}
                
                # N-Effect logs may not have DM_Build_s, so we handle its absence.
                dm_build_s = float(parts.get('DM_Build_s', -1.0))
                clustering_s = float(parts['Clustering_s'])

                record = {
                    'Nodes': int(parts['Nodes']),
                    'Clusters': int(parts['Clusters']),
                    'DM_Build_s': dm_build_s,
                    'Clustering_s': clustering_s
                }

                # If DM_Build_s is not present, Total_Time_s is just Clustering_s
                if dm_build_s == -1.0:
                    record['Total_Time_s'] = clustering_s
                else:
                    record['Total_Time_s'] = dm_build_s + clustering_s
                
                records.append(record)
            except (KeyError, ValueError, IndexError) as e:
                print(f"Skipping malformed line: {line} -> {e}")
            
    return pd.DataFrame(records)

def generate_n_effect_plot(df):
    """Generates and saves the N-effect plot."""
    if df.empty:
        print("DataFrame is empty. No N-effect data found to plot.")
        return

    # Ensure data is sorted by Nodes for plotting
    df = df.sort_values('Nodes')

    print("--- Data for Plot ---")
    print(df[['Nodes', 'DM_Build_s', 'Clustering_s', 'Total_Time_s']])

    plt.figure(figsize=(12, 7))
    
    # Only plot DM_Build_s if it contains valid data (not all -1.0)
    if not (df['DM_Build_s'] == -1.0).all():
        plt.plot(df['Nodes'], df['DM_Build_s'], marker='o', linestyle='-', label='Pass 1: DM Build')
        
    plt.plot(df['Nodes'], df['Clustering_s'], marker='s', linestyle='-', label='Pass 2-3: Clustering')
    plt.plot(df['Nodes'], df['Total_Time_s'], marker='^', linestyle='--', label='Total Runtime', color='black')
    
    plt.title(f'HSM-Cluster: Effect of Dataset Size (N) on Runtime')
    plt.xlabel('Number of Nodes (N)')
    plt.ylabel('Runtime (seconds)')
    plt.xscale('log')
    plt.yscale('log')
    plt.grid(True, which="both", ls="--")
    plt.legend()
    
    # Annotate total time points
    for i, row in df.iterrows():
        plt.text(row['Nodes'], row['Total_Time_s'], f'{row["Total_Time_s"]:.2f}s', fontsize=9, ha='left', va='bottom')

    plot_path = os.path.join(OUTPUT_DIR, 'figure_n_effect.png')
    plt.savefig(plot_path)
    print(f"\nPlot saved to: {plot_path}")

def main():
    """Main function to parse data and generate plots."""
    if not os.path.exists(LOG_FILE):
        print(f"Error: Log file not found at {LOG_FILE}")
        print("Please run the 'Run N-Effect Experiment' script first.")
        return

    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    df = parse_log_file(LOG_FILE)
    generate_n_effect_plot(df)

if __name__ == '__main__':
    main()
