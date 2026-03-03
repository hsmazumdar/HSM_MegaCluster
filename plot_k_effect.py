import pandas as pd
import matplotlib.pyplot as plt
import os

# --- Configuration ---
LOG_FILE = os.path.join(os.path.dirname(__file__), 'results', 'k_effect_log.txt')
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'results')

def parse_log_file(log_path):
    """Parses the performance log file for K-effect data and returns a pandas DataFrame."""
    records = []
    with open(log_path, 'r') as f:
        for line in f:
            line = line.strip()
            # K-effect logs must contain 'K:'
            if not line or 'K:' not in line:
                continue
            
            try:
                parts = {p.split(':')[0].strip(): p.split(':')[1].strip() for p in line.split(',')}
                record = {
                    'Nodes': int(parts['Nodes']),
                    'Clusters': int(parts['Clusters']),
                    'K': int(parts['K']),
                    'Clustering_s': float(parts['Clustering_s'])
                }
                # For K-effect, the total time is simply the clustering time.
                record['Total_Time_s'] = record['Clustering_s']
                records.append(record)
            except (KeyError, ValueError, IndexError) as e:
                print(f"Skipping malformed line: {line} -> {e}")
            
    return pd.DataFrame(records)


def generate_k_effect_plot(df):
    """Generates and saves the K-effect plot."""
    if df.empty:
        print("DataFrame is empty. No K-effect data found to plot.")
        return

    # Ensure data is sorted by K for plotting
    df = df.sort_values('K')

    print("--- Data for Plot ---")
    # Display only the relevant columns for this plot
    print(df[['K', 'Clustering_s', 'Total_Time_s']])

    plt.figure(figsize=(12, 7))
    
    # The K-Effect plot focuses only on the clustering pass, not the DM Build pass.
    plt.plot(df['K'], df['Clustering_s'], marker='s', linestyle='-', label='Clustering Runtime (Pass 2-3)')
    
    plt.title(f'HSM-Cluster: Effect of Neighborhood Size (K) on Runtime (N={df["Nodes"].iloc[0]})')
    plt.xlabel('Neighborhood Size (K)')
    plt.ylabel('Runtime (seconds)')
    plt.grid(True, which="both", ls="--")
    plt.legend()
    
    # Annotate total time points
    for i, row in df.iterrows():
        plt.text(row['K'], row['Clustering_s'], f'{row["Clustering_s"]:.2f}s', fontsize=9, ha='left', va='bottom')

    plot_path = os.path.join(OUTPUT_DIR, 'figure2_k_effect.png')
    plt.savefig(plot_path)
    print(f"\nPlot saved to: {plot_path}")

def main():
    """Main function to parse data and generate plots."""
    if not os.path.exists(LOG_FILE):
        print(f"Error: Log file not found at {LOG_FILE}")
        print("Please run the data_gen_k.py script first.")
        return

    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)

    df = parse_log_file(LOG_FILE)
    generate_k_effect_plot(df)

if __name__ == '__main__':
    main()
