"""
This script automates the process of running a series of clustering experiments
for performance analysis. It uses a compiled C# executable (`MazCluster.exe`)
to perform the clustering and generates individual CSV files for each experiment's
results, as well as a consolidated performance log.

The main purpose is to gather data on how the clustering algorithm's runtime
scales with the number of data points (nodes).

Author: Himanshu S. Mazumdar
Date: 2026-03-03
Version: 1.0

Key components:
- Configuration: Defines the path to the executable and the output directory.
- Experiments: A list of dictionaries, each specifying the parameters for one
  experiment (e.g., number of nodes and clusters).
- `run_experiment`: A function that constructs and executes the command-line
  call to `MazCluster.exe` for a single experiment.
- `main`: The main function that creates the output directory, iterates through
  the defined experiments, and calls `run_experiment` for each.
"""
import subprocess
import os

# --- Configuration ---
# This section defines the paths and parameters used for the experiments.
# Reviewers should ensure these paths are correct for their environment.

# Path to the C# executable that performs the clustering.
# This is expected to be in the same directory as this Python script.
EXE_PATH = os.path.join(
    os.path.dirname(__file__),
    "MazCluster.exe",
)

# Directory where the output CSV files and performance log will be saved.
# A "results" folder will be created in the same directory as this script.
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "results")

# --- Experiment Definitions ---
# This list defines the different scenarios to be tested. Each dictionary
# represents a single run of the `MazCluster.exe` with specific parameters.
# The primary variable being tested here is the number of 'nodes'.
EXPERIMENTS = [
    {"nodes": 1000, "clusters": 100},
    {"nodes": 2000, "clusters": 100},
    {"nodes": 5000, "clusters": 100},
    {"nodes": 10000, "clusters": 100},
    {"nodes": 20000, "clusters": 100},
    {"nodes": 50000, "clusters": 100},
    {"nodes": 100000, "clusters": 100},
    {"nodes": 200000, "clusters": 100},
    {"nodes": 500000, "clusters": 100},
    # Additional experiments can be uncommented for more extensive testing.
    # based on RAM available in test computer up to 32GB or 64Gb
    {"nodes": 1000000, "clusters": 100},
    {"nodes": 2000000, "clusters": 100},
    {"nodes": 5000000, "clusters": 100},
    {"nodes": 10000000, "clusters": 100},
    {"nodes": 15000000, "clusters": 100},
    {"nodes": 20000000, "clusters": 100},
    {"nodes": 25000000, "clusters": 100},
    {"nodes": 30000000, "clusters": 100},
    {"nodes": 35000000, "clusters": 100},
]


def run_experiment(nodes, clusters, output_file, log_callback):
    """
    Runs a single clustering experiment using the C# executable.

    This function constructs the command-line arguments, executes the
    `MazCluster.exe` process, and captures its output. It also specifies
    the path for the consolidated performance log file.

    Args:
        nodes (int): The number of data points to generate and cluster.
        clusters (int): The number of clusters to form.
        output_file (str): The path to save the detailed CSV output for this
                           specific experiment.
        log_callback (function): A function to call for logging output.
    """
    log_callback(f"--- Running Experiment: Nodes={nodes}, Clusters={clusters} ---")

    # Define the absolute path for the performance log file.
    # This file will contain a summary of performance metrics for all experiments.
    log_file_path = os.path.join(OUTPUT_DIR, 'performance_log.txt')

    # Construct the command to be executed. This includes the path to the
    # executable and all necessary command-line arguments.
    command = [
        EXE_PATH,
        "--nodes", str(nodes),
        "--clusters", str(clusters),
        "--output", output_file,
        "--logfile", log_file_path,
    ]

    # The executable must be run from its own directory to find its dependencies.
    exe_dir = os.path.dirname(EXE_PATH)

    try:
        # Execute the command as a separate process.
        # `subprocess.Popen` is used to capture stdout and stderr.
        # `cwd` is set to the executable's directory.
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            cwd=exe_dir,
        )

        # Stream the output in real-time
        while True:
            output = process.stdout.readline()
            if output == '' and process.poll() is not None:
                break
            if output:
                log_callback(output.strip())
        
        # Final check on the return code
        rc = process.poll()
        if rc == 0:
            # Further validation: ensure the output file was actually created.
            if os.path.exists(output_file) and os.path.getsize(output_file) > 0:
                log_callback(f"Experiment finished successfully. Results saved to {output_file}")
            else:
                log_callback("Error: Experiment finished with exit code 0, but output file is missing or empty.")
        else:
            log_callback(f"Error: Experiment failed with exit code {rc}")

    except FileNotFoundError:
        log_callback(f"Error: Executable not found at {EXE_PATH}")
        log_callback("Please ensure you have built the C# project and the .exe is in the correct location.")
    except subprocess.TimeoutExpired:
        log_callback(f"Error: Experiment timed out after {36000} seconds.")
        process.kill()
        stdout, stderr = process.communicate()
        if stdout:
            log_callback("[STDOUT after timeout]")
            log_callback(stdout)
        if stderr:
            log_callback("[STDERR after timeout]")
            log_callback(stderr)
    except Exception as e:
        log_callback(f"An unexpected error occurred: {e}")

    log_callback("--------------------------------------------------\n")


def run_data_generation(log_callback):
    """
    Main function to orchestrate the data generation process.
    """
    log_callback("Starting data generation for HSM-Cluster paper.")
    log_callback(f"Using executable: {EXE_PATH}")

    # Create the output directory if it doesn't already exist.
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        log_callback(f"Created output directory: {OUTPUT_DIR}")

    # Clear the old performance log at the beginning of a new run.
    log_file_path = os.path.join(OUTPUT_DIR, 'performance_log.txt')
    if os.path.exists(log_file_path):
        os.remove(log_file_path)
        log_callback("Cleared old performance log file.")

    # Iterate through all defined experiments and run them sequentially.
    for i, exp in enumerate(EXPERIMENTS):
        nodes = exp["nodes"]
        clusters = exp["clusters"]
        
        # Define a unique output filename for each experiment's detailed results.
        output_file = os.path.join(OUTPUT_DIR, f"results_n{nodes}_c{clusters}.csv")
        
        run_experiment(nodes, clusters, output_file, log_callback)

    log_callback("All experiments completed.")


def main():
    """
    Main function to orchestrate the data generation process.
    """
    run_data_generation(print)


if __name__ == "__main__":
    # This ensures the main function is called only when the script is executed directly.
    main()
