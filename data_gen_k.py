import subprocess
import os

# --- Configuration ---
# Path to the C# executable
EXE_PATH = os.path.join(os.path.dirname(__file__),  'MazCluster.exe')

# Directory to save the output CSV files
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'results')

# --- Experiments ---
# Define the list of K values to test for a fixed N.
# As per HSM-MegaCluster.txt, Section 4.3
FIXED_NODES = 1000000
FIXED_CLUSTERS = 50
K_VALUES = [10, 20, 50, 100, 200, 500]


def run_experiment(nodes, clusters, k, output_file):
    """Runs a single clustering experiment using the C# executable."""
    print(f'--- Running Experiment: Nodes={nodes}, Clusters={clusters}, K={k} ---')
    
    exe_dir = os.path.dirname(EXE_PATH)
    log_file_path = os.path.join(OUTPUT_DIR, 'k_effect_log.txt')

    command = [
        EXE_PATH,
        '--nodes', str(nodes),
        '--clusters', str(clusters),
        '--k', str(k),
        '--output', output_file,
        '--logfile', log_file_path
    ]

    print(f'DEBUG: Executing command: {" ".join(command)}')
    print(f'DEBUG: CWD: {exe_dir}')

    try:
        # Execute the command and capture the output in real-time
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8', cwd=exe_dir)

        # Stream stdout
        print("--- C# Process STDOUT ---")
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                print(output.strip(), flush=True)
        
        # Capture stderr
        print("--- C# Process STDERR ---")
        stderr_output = process.stderr.read()
        if stderr_output:
            print(stderr_output.strip(), flush=True)
        else:
            print("(No errors reported)")

        rc = process.poll()
        print(f'DEBUG: Process finished with exit code {rc}')

        if rc == 0:
            # Add a check for the output file size
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                print(f'SUCCESS: Experiment finished. CSV results saved to {output_file}')
            else:
                print(f'ERROR: Process exited 0, but output file is missing or empty: {output_file}')
        else:
            print(f'ERROR: Experiment failed with non-zero exit code: {rc}')

    except FileNotFoundError:
        print(f'Error: Executable not found at {EXE_PATH}')
        print('Please ensure you have built the C# project.')
    except Exception as e:
        print(f'An unexpected error occurred: {e}')

    print('-' * 50 + '\n')

def main():
    """Main function to run all defined experiments."""
    print('Starting K-effect data generation for HSM-Cluster paper.')
    print(f'Using executable: {EXE_PATH}')
    
    if not os.path.exists(EXE_PATH):
        print(f'Error: Executable not found. Please build the C# project in Debug mode.')
        return

    # Create the output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        print(f'Created output directory: {OUTPUT_DIR}')

    # Clear the old log file at the beginning of a new run
    log_file_path = os.path.join(OUTPUT_DIR, 'k_effect_log.txt')
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
        print("Cleared old K-effect log file.")

    for k_value in K_VALUES:
        output_filename = f'results_n{FIXED_NODES}_k{k_value}.csv'
        output_filepath = os.path.join(OUTPUT_DIR, output_filename)
        
        run_experiment(FIXED_NODES, FIXED_CLUSTERS, k_value, output_filepath)

    print('All K-effect experiments completed.')

if __name__ == '__main__':
    main()
