

"""
This script provides a graphical user interface (GUI) for running a suite of
clustering experiments and visualizing the results. It serves as a centralized
dashboard for the "Mega Cluster" analysis tools.

Author: Himanshu S. Mazumdar
Date: 2026-03-03
Version: 1.1

The application is built using tkinter and is organized into a series of tabs,
each dedicated to a specific task:
- Analysis: The main tab for running the full data generation and plotting
  workflow. It directly calls the core logic from `data_gen.py` and
  `plot_results.py`.
- N-Effect Analysis: Runs experiments and plots focusing on the effect of the
  number of data points (N).
- K-Effect Analysis: Runs experiments and plots focusing on the effect of the
  number of clusters (K).
- General Results: A dedicated tab for plotting the main runtime scaling results.
- MazCluster Runner: A simple interface to run the `MazCluster.exe` executable
  directly and view its raw output.

Key Features:
- Asynchronous Execution: All external scripts and executables are run in
  separate threads to keep the GUI responsive.
- Real-time Logging: Output from running processes is streamed in real-time to
  scrolled text widgets in each tab.
- Integrated Plotting: Generated plots can be automatically displayed in a new
  window.
- Modular Design: The GUI is built with a clear, tab-based structure, and the
  core analysis logic is imported from other scripts, promoting code reuse.
"""
import tkinter as tk
from tkinter import ttk, scrolledtext
import subprocess
import os
import threading
import pandas as pd
from PIL import Image, ImageTk
from data_gen import run_data_generation
from plot_results import run_plotting

class MegaClusterHero(tk.Tk):
    """
    The main application class for the Mega Cluster Hero GUI.
    This class initializes the main window, creates the tabbed interface,
    and defines the methods for handling user interactions.
    """
    def __init__(self):
        """
        Initializes the main application window, sets the title, size,
        and creates all the necessary tabs.
        """
        super().__init__()
        self.title("Mazumdar's Mega Cluster")
        self.geometry("800x600")

        # Configure the style for the notebook tabs to be bold and colorful.
        style = ttk.Style()
        style.configure("TNotebook.Tab", font=('Helvetica', '10', 'bold'), padding=[10, 5])
        style.map("TNotebook.Tab", foreground=[("selected", "#0078D7"), ("!selected", "#555555")])

        # Create the main notebook widget to hold all the tabs.
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(pady=10, padx=10, fill="both", expand=True)

        # Initialize each of the application's tabs.
        self.create_analysis_tab()
        self.create_n_effect_tab()
        self.create_k_effect_tab()
        self.create_results_tab()
        self.create_mazcluster_tab()

    def create_analysis_tab(self):
        """
        Creates the 'Analysis' tab.
        This is the primary tab for the integrated workflow, allowing the user to
        run data generation and plotting from the imported script functions.
        """
        self.analysis_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.analysis_tab, text="Full Workflow")

        button_frame = ttk.Frame(self.analysis_tab)
        button_frame.pack(pady=10)

        # Button to trigger the data generation process.
        run_button = ttk.Button(button_frame, text="Run Data Generation", command=self.run_data_generation_thread)
        run_button.pack(side="left", padx=5)

        # Button to trigger the plotting process.
        plot_button = ttk.Button(button_frame, text="Generate Plots", command=self.run_plotting_thread)
        plot_button.pack(side="left", padx=5)

        # Scrolled text widget for displaying logs from the analysis workflow.
        self.analysis_log_text = scrolledtext.ScrolledText(self.analysis_tab, width=80, height=20)
        self.analysis_log_text.pack(pady=10, padx=10, fill="both", expand=True)

    def log_to_widget(self, message, widget):
        """
        A helper function to safely log messages to a tkinter text widget
        from different threads.
        """
        widget.insert(tk.END, message + "\n")
        widget.see(tk.END)

    def run_data_generation_thread(self):
        """
        Starts the data generation process in a new thread to avoid blocking
        the GUI. The output is logged to the 'Analysis' tab.
        """
        self.analysis_log_text.delete(1.0, tk.END)
        # The `run_data_generation` function is imported from `data_gen.py`.
        # A lambda function is used to pass the logging callback.
        thread = threading.Thread(target=run_data_generation, args=(lambda msg: self.log_to_widget(msg, self.analysis_log_text),))
        thread.start()

    def run_plotting_thread(self):
        """
        Starts the plotting process in a new thread.
        """
        self.analysis_log_text.delete(1.0, tk.END)
        thread = threading.Thread(target=self.run_plotting_and_display)
        thread.start()

    def log_message(self, message, widget):
        """
        Helper to log a message to a widget, ensuring it's thread-safe.
        """
        widget.insert(tk.END, message)
        widget.see(tk.END)

    def run_plotting_and_display(self):
        """
        Calls the imported plotting function and, if successful, displays
        the resulting plot in a new window.
        """
        # The `run_plotting` function is imported from `plot_results.py`.
        plot_path = run_plotting(lambda msg: self.log_to_widget(msg, self.analysis_log_text))
        if plot_path and os.path.exists(plot_path):
            self.display_plot(plot_path, self.analysis_log_text)

    def create_n_effect_tab(self):
        """
        Creates the 'N-Effect Analysis' tab.
        This tab provides buttons to run the standalone `data_gen.py` and
        `plot_n_effect.py` scripts.
        """
        self.n_effect_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.n_effect_tab, text="N-Effect Analysis")

        button_frame = ttk.Frame(self.n_effect_tab)
        button_frame.pack(pady=10)

        run_button = ttk.Button(button_frame, text="Run N-Effect Experiment", command=lambda: self.run_script_thread('data_gen.py', self.n_log_text))
        run_button.pack(side="left", padx=5)

        plot_button = ttk.Button(button_frame, text="Plot N-Effect", command=lambda: self.run_script_thread('plot_n_effect.py', self.n_log_text, 'results/figure_n_effect.png'))
        plot_button.pack(side="left", padx=5)

        self.n_log_text = scrolledtext.ScrolledText(self.n_effect_tab, width=80, height=20)
        self.n_log_text.pack(pady=10, padx=10, fill="both", expand=True)

    def create_k_effect_tab(self):
        """
        Creates the 'K-Effect Analysis' tab.
        This tab provides buttons to run the standalone `data_gen_k.py` and
        `plot_k_effect.py` scripts.
        """
        self.k_effect_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.k_effect_tab, text="K-Effect Analysis")

        button_frame = ttk.Frame(self.k_effect_tab)
        button_frame.pack(pady=10)

        run_button = ttk.Button(button_frame, text="Run K-Effect Experiment", command=lambda: self.run_script_thread('data_gen_k.py', self.k_log_text))
        run_button.pack(side="left", padx=5)

        plot_button = ttk.Button(button_frame, text="Plot K-Effect", command=lambda: self.run_script_thread('plot_k_effect.py', self.k_log_text, 'results/figure2_k_effect.png'))
        plot_button.pack(side="left", padx=5)

        self.k_log_text = scrolledtext.ScrolledText(self.k_effect_tab, width=80, height=20)
        self.k_log_text.pack(pady=10, padx=10, fill="both", expand=True)

    def create_results_tab(self):
        """
        Creates the 'Results Dashboard' tab.
        This tab displays summary tables of N-Effect and K-Effect experiments
        and provides buttons to refresh the data and plot the main results.
        """
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Results Dashboard")

        # --- Button Frame ---
        button_frame = ttk.Frame(self.results_tab)
        button_frame.pack(pady=10, fill='x')

        refresh_button = ttk.Button(button_frame, text="Refresh Data", command=self.load_results_data)
        refresh_button.pack(side="left", padx=10)

        plot_button = ttk.Button(button_frame, text="Plot General Results", command=lambda: self.run_script_thread('plot_results.py', self.analysis_log_text, 'results/figure1_runtime_scaling.png'))
        plot_button.pack(side="left", padx=5)
        
        self.status_label = ttk.Label(button_frame, text="Click 'Refresh Data' to load results.")
        self.status_label.pack(side="left", padx=10)

        # --- Paned Window for Tables ---
        paned_window = ttk.PanedWindow(self.results_tab, orient=tk.VERTICAL)
        paned_window.pack(fill="both", expand=True, padx=10, pady=5)

        # --- N-Effect Table ---
        n_effect_frame = ttk.LabelFrame(paned_window, text="N-Effect Results (from performance_log.txt)")
        paned_window.add(n_effect_frame, weight=1)

        self.n_effect_tree = ttk.Treeview(n_effect_frame, show='headings')
        self.n_effect_tree.pack(fill="both", expand=True)

        # --- K-Effect Table ---
        k_effect_frame = ttk.LabelFrame(paned_window, text="K-Effect Results (from k_effect_log.txt)")
        paned_window.add(k_effect_frame, weight=1)

        self.k_effect_tree = ttk.Treeview(k_effect_frame, show='headings')
        self.k_effect_tree.pack(fill="both", expand=True)

    def load_results_data(self):
        """
        Loads data from log files and populates the Treeview tables.
        """
        self.status_label.config(text="Loading data...")
        self.update_idletasks()

        # --- Load N-Effect Data ---
        try:
            n_log_path = os.path.join(os.path.dirname(__file__), 'results', 'performance_log.txt')
            
            records = []
            with open(n_log_path, 'r') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        parts = {p.split(':')[0].strip(): p.split(':')[1].strip() for p in line.split(',')}
                        records.append(parts)
                    except IndexError:
                        print(f"Skipping malformed line in N-Effect log: {line.strip()}")

            if records:
                n_df = pd.DataFrame(records)
                cols = ['Nodes', 'Clusters', 'DM_Build_s', 'Clustering_s', 'Total_Time_s']
                n_df = n_df.reindex(columns=cols).fillna('N/A')
                self._populate_treeview(self.n_effect_tree, n_df)
            else:
                 self._populate_treeview(self.n_effect_tree, pd.DataFrame(), "No data found.")

        except FileNotFoundError:
            self._populate_treeview(self.n_effect_tree, pd.DataFrame(), "Log file not found.")
        except Exception as e:
            error_df = pd.DataFrame([{"Error": str(e)}])
            self._populate_treeview(self.n_effect_tree, error_df)

        # --- Load K-Effect Data ---
        try:
            k_log_path = os.path.join(os.path.dirname(__file__), 'results', 'k_effect_log.txt')
            records = []
            with open(k_log_path, 'r') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        parts = {p.split(':')[0].strip(): p.split(':')[1].strip() for p in line.split(',')}
                        records.append(parts)
                    except IndexError:
                        print(f"Skipping malformed line in K-Effect log: {line.strip()}")

            if records:
                k_df = pd.DataFrame(records)
                cols = ['Nodes', 'Clusters', 'K', 'Clustering_s']
                k_df = k_df.reindex(columns=cols).fillna('N/A')
                self._populate_treeview(self.k_effect_tree, k_df)
            else:
                self._populate_treeview(self.k_effect_tree, pd.DataFrame(), "No data found.")

        except FileNotFoundError:
            self._populate_treeview(self.k_effect_tree, pd.DataFrame(), "Log file not found.")
        except Exception as e:
            error_df = pd.DataFrame([{"Error": str(e)}])
            self._populate_treeview(self.k_effect_tree, error_df)
            
        self.status_label.config(text="Data loaded.")

    def _populate_treeview(self, tree, df, empty_message=None):
        """Helper to clear and populate a Treeview with a DataFrame."""
        for i in tree.get_children():
            tree.delete(i)
        
        if df.empty and empty_message:
            tree["columns"] = ("Status",)
            tree.heading("Status", text="Status")
            tree.column("Status", anchor="center")
            tree.insert("", "end", values=(empty_message,))
            return

        tree["columns"] = list(df.columns)
        tree["show"] = "headings"

        for col in df.columns:
            tree.heading(col, text=col)
            tree.column(col, anchor="center", width=100)

        for index, row in df.iterrows():
            tree.insert("", "end", values=list(row))

    def create_mazcluster_tab(self):
        """
        Creates the 'MazCluster Runner' tab.
        This provides a simple interface for running the `MazCluster.exe`
        executable directly and viewing its raw output.
        """
        self.mazcluster_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.mazcluster_tab, text="MazCluster Runner")

        run_button = ttk.Button(self.mazcluster_tab, text="RUN", command=self.run_mazcluster)
        run_button.pack(pady=10)

        self.mazcluster_log_text = scrolledtext.ScrolledText(self.mazcluster_tab, width=80, height=20)
        self.mazcluster_log_text.pack(pady=10, padx=10, fill="both", expand=True)

    def run_mazcluster(self):
        """
        Executes the `MazCluster.exe` file and streams its output to the
        corresponding log widget. This runs in the main thread and will block
        until the executable finishes.
        """
        exe_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'MazCluster.exe')
        exe_dir = os.path.dirname(exe_path)

        self.mazcluster_log_text.delete(1.0, tk.END)
        self.mazcluster_log_text.insert(tk.END, f"Running {exe_path}...\n")
        self.update_idletasks()

        try:
            # Run the executable in a separate process.
            process = subprocess.Popen([exe_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, encoding='utf-8', cwd=exe_dir)

            # Read and display the output line by line in real-time.
            while True:
                output = process.stdout.readline()
                if output == '' and process.poll() is not None:
                    break
                if output:
                    self.mazcluster_log_text.insert(tk.END, output)
                    self.mazcluster_log_text.see(tk.END)
                    self.update_idletasks()

            self.mazcluster_log_text.insert(tk.END, f"\nMazCluster.exe finished.\n")

        except Exception as e:
            self.mazcluster_log_text.insert(tk.END, f"\nError running MazCluster.exe: {e}\n")

    def run_script_thread(self, script_name, log_widget, plot_path=None):
        """
        Runs a script in a separate thread to keep the GUI responsive,
        streaming its output to the provided text widget.
        """
        def task():
            self.after(0, lambda: log_widget.delete(1.0, tk.END))
            self.after(0, lambda: self.log_message(f"Running {script_name}...\n", log_widget))
            
            try:
                script_path = os.path.join(os.path.dirname(__file__), script_name)
                project_root = os.path.dirname(__file__)

                process = subprocess.Popen(
                    ["python", "-u", script_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding='utf-8',
                    cwd=project_root
                )

                for line in iter(process.stdout.readline, ''):
                    self.after(0, lambda l=line: self.log_message(l, log_widget))
                
                process.stdout.close()
                process.wait()

                self.after(0, lambda: self.log_message(f"\n{script_name} finished.\n", log_widget))

                if plot_path:
                    full_plot_path = os.path.join(project_root, plot_path)
                    if os.path.exists(full_plot_path):
                        self.after(0, lambda: self.display_plot(full_plot_path, log_widget))

            except Exception as e:
                error_message = f"\nAn unexpected error occurred with {script_name}:\n{str(e)}\n"
                self.after(0, lambda: self.log_message(error_message, log_widget))

        thread = threading.Thread(target=task)
        thread.daemon = True
        thread.start()

    def display_plot(self, plot_path, text_widget):
        """
        Opens a new Toplevel window to display a specified image file.
        """
        try:
            # Create a new window to display the plot.
            plot_window = tk.Toplevel(self)
            plot_window.title(f"Plot - {os.path.basename(plot_path)}")

            img = Image.open(plot_path)
            img = ImageTk.PhotoImage(img)

            panel = tk.Label(plot_window, image=img)
            panel.image = img # Keep a reference to avoid garbage collection.
            panel.pack(side="bottom", fill="both", expand="yes")

        except Exception as e:
            text_widget.insert(tk.END, f"\nError displaying plot: {e}\n")

if __name__ == "__main__":
    # Entry point for the application.
    app = MegaClusterHero()
    app.mainloop()
