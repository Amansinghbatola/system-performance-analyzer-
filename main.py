# main.py

import tkinter as tk
from tkinter import ttk
import system_monitor_manual as sm_manual # Import our manual monitoring logic
import time

class SystemAnalyzerGUI:
    def __init__(self, master):
        self.master = master
        master.title("System Performance Analyzer (Manual Calc)")
        master.geometry("800x700")
        master.resizable(True, True)

        # Initialize manual counters by doing a dummy call
        # This primes the internal counters in system_monitor_manual
        _ = sm_manual.calculate_cpu_usage()
        _ = sm_manual.calculate_network_io_rates()
        _ = sm_manual.calculate_process_cpu_usage()

        # --- Styles ---
        self.style = ttk.Style()
        self.style.theme_use('clam')
        self.style.configure('TFrame', background='#e0f2f7')
        self.style.configure('TLabel', background='#e0f2f7', foreground='#333')
        self.style.configure('TProgressbar', thickness=15)
        # We can't dynamically change progress bar colors easily with ttk.Style.map based on value
        # without defining multiple styles (e.g., 'red.Horizontal.TProgressbar', 'green.Horizontal.TProgressbar')
        # For simplicity, we'll keep it fixed, or you can implement a custom drawing.

        # --- Main Frame ---
        self.main_frame = ttk.Frame(master, padding="15", style='TFrame')
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Section: Basic Metrics ---
        self.metrics_frame = ttk.LabelFrame(self.main_frame, text="System Overview", padding="10")
        self.metrics_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=10)

        # CPU
        ttk.Label(self.metrics_frame, text="CPU Usage:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.cpu_label = ttk.Label(self.metrics_frame, text="--%")
        self.cpu_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        self.cpu_progress = ttk.Progressbar(self.metrics_frame, orient="horizontal", length=200, mode="determinate")
        self.cpu_progress.grid(row=0, column=2, sticky="ew", padx=5, pady=2)

        # Memory
        ttk.Label(self.metrics_frame, text="Memory Usage:").grid(row=1, column=0, sticky="w", padx=5, pady=2)
        self.mem_label = ttk.Label(self.metrics_frame, text="--% (--GB / --GB)")
        self.mem_label.grid(row=1, column=1, sticky="w", padx=5, pady=2)
        self.mem_progress = ttk.Progressbar(self.metrics_frame, orient="horizontal", length=200, mode="determinate")
        self.mem_progress.grid(row=1, column=2, sticky="ew", padx=5, pady=2)

        # Disk
        ttk.Label(self.metrics_frame, text="Disk Usage:").grid(row=2, column=0, sticky="w", padx=5, pady=2)
        self.disk_label = ttk.Label(self.metrics_frame, text="--% (--GB / --GB)")
        self.disk_label.grid(row=2, column=1, sticky="w", padx=5, pady=2)
        self.disk_progress = ttk.Progressbar(self.metrics_frame, orient="horizontal", length=200, mode="determinate")
        self.disk_progress.grid(row=2, column=2, sticky="ew", padx=5, pady=2)

        # Network I/O
        ttk.Label(self.metrics_frame, text="Network I/O:").grid(row=3, column=0, sticky="w", padx=5, pady=2)
        self.net_label = ttk.Label(self.metrics_frame, text="Sent: -- KB/s, Recv: -- KB/s")
        self.net_label.grid(row=3, column=1, columnspan=2, sticky="w", padx=5, pady=2)

        # Uptime and Last Updated
        self.info_frame = ttk.Frame(self.main_frame, style='TFrame')
        self.info_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=10)
        ttk.Label(self.info_frame, text="Uptime:").grid(row=0, column=0, sticky="w", padx=5, pady=2)
        self.uptime_label = ttk.Label(self.info_frame, text="--")
        self.uptime_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
        ttk.Label(self.info_frame, text="Last Updated:").grid(row=0, column=2, sticky="w", padx=5, pady=2)
        self.last_updated_label = ttk.Label(self.info_frame, text="--")
        self.last_updated_label.grid(row=0, column=3, sticky="w", padx=5, pady=2)


        # --- Section: Top Processes ---
        self.process_frame = ttk.LabelFrame(self.main_frame, text="Top Processes (by CPU)", padding="10")
        self.process_frame.grid(row=2, column=0, columnspan=2, sticky="nsew", pady=10)
        self.main_frame.grid_rowconfigure(2, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Treeview for processes
        self.process_tree = ttk.Treeview(self.process_frame, columns=("PID", "Name", "CPU%", "Mem%", "Threads", "User"), show="headings")
        self.process_tree.heading("PID", text="PID")
        self.process_tree.heading("Name", text="Name")
        self.process_tree.heading("CPU%", text="CPU%")
        self.process_tree.heading("Mem%", text="Mem%")
        self.process_tree.heading("Threads", text="Threads")
        self.process_tree.heading("User", text="User")

        self.process_tree.column("PID", width=60, anchor=tk.CENTER)
        self.process_tree.column("Name", width=200, anchor=tk.W)
        self.process_tree.column("CPU%", width=70, anchor=tk.CENTER)
        self.process_tree.column("Mem%", width=70, anchor=tk.CENTER)
        self.process_tree.column("Threads", width=80, anchor=tk.CENTER)
        self.process_tree.column("User", width=120, anchor=tk.W)

        self.process_tree.pack(fill=tk.BOTH, expand=True)

        # Scrollbar for the Treeview
        vsb = ttk.Scrollbar(self.process_frame, orient="vertical", command=self.process_tree.yview)
        vsb.pack(side='right', fill='y')
        self.process_tree.configure(yscrollcommand=vsb.set)


        # --- Refresh Rate ---
        self.refresh_interval_ms = 3000 # Refresh every 3 seconds (milliseconds)
        self.update_data() # Initial call to populate data

    def update_data(self):
        """Fetches and updates all performance data in the GUI using manual calculations."""
        # CPU (manual calculation)
        cpu_usage = sm_manual.calculate_cpu_usage()
        self.cpu_label.config(text=f"{cpu_usage:.1f}%")
        self.cpu_progress['value'] = cpu_usage

        # Memory (psutil.virtual_memory().percent is already (used/total)*100)
        mem_info = sm_manual.get_memory_info()
        self.mem_label.config(text=f"{mem_info['percentage']:.1f}% ({mem_info['used_gb']:.2f}GB / {mem_info['total_gb']:.2f}GB)")
        self.mem_progress['value'] = mem_info['percentage']

        # Disk (psutil.disk_usage().percent is already (used/total)*100)
        disk_info = sm_manual.get_disk_usage()
        self.disk_label.config(text=f"{disk_info['percentage']:.1f}% ({disk_info['used_gb']:.2f}GB / {disk_info['total_gb']:.2f}GB)")
        self.disk_progress['value'] = disk_info['percentage']

        # Network I/O (manual calculation)
        net_io = sm_manual.calculate_network_io_rates()
        self.net_label.config(text=f"Sent: {net_io['sent_kbps']:.2f} KB/s, Recv: {net_io['recv_kbps']:.2f} KB/s")

        # Uptime (manual calculation using psutil.boot_time())
        self.uptime_label.config(text=sm_manual.get_system_uptime())
        self.last_updated_label.config(text=time.strftime("%H:%M:%S"))

        # Top Processes (manual calculation of CPU%)
        self.process_tree.delete(*self.process_tree.get_children()) # Clear existing rows
        top_processes = sm_manual.calculate_process_cpu_usage()
        for p in top_processes:
            self.process_tree.insert("", tk.END, values=(p['pid'], p['name'], f"{p['cpu_percent']:.1f}", f"{p['memory_percent']:.1f}", p['threads'], p['user']))

        # Schedule the next update
        self.master.after(self.refresh_interval_ms, self.update_data)

def main():
    root = tk.Tk()
    app = SystemAnalyzerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()