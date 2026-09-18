import os
import subprocess
import urllib.request
import ssl
import threading
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
from datetime import datetime

# CONFIGURATION
# Update this with your verified Web App URL ending in /exec
GAS_URL = "https://script.google.com/a/macros/broadcom.com/s/AKfycbyWtivODxxatPlG3JBRdwJ_ual9ELwOKCV-OnaztbIIf6OXlvdNF_FX3t75S-TiRA/exec "  
PYTHON_FTP_SCRIPT = r"G:\My Drive\claude code work\wafer_ftp_puller\ftp_puller_maxlimit_folders.py"

class WaferControlPanel:
    def __init__(self, root):
        self.root = root
        self.root.title("Wafer Data Puller - Control Panel")
        self.root.geometry("650x480")
        self.root.resizable(False, False)

        # Style
        style = ttk.Style()
        style.theme_use('clam')

        # Header Title
        title_lbl = ttk.Label(root, text="Wafer Probing Automation System", font=("Segoe UI", 14, "bold"))
        title_lbl.pack(pady=(15, 5))

        # Schedule Status Banner
        status_frame = ttk.LabelFrame(root, text=" Automation Status ")
        status_frame.pack(fill="x", padx=20, pady=5)
        
        status_lbl = ttk.Label(
            status_frame, 
            text="🟢 AUTO-SCHEDULE ACTIVE: Daily run scheduled for 12:00 PM (Noon)", 
            foreground="darkgreen", 
            font=("Segoe UI", 9, "bold")
        )
        status_lbl.pack(padx=10, pady=8)

        # Action Buttons Frame (Manual Override)
        btn_frame = ttk.LabelFrame(root, text=" Manual Control (On-Demand Execution) ")
        btn_frame.pack(fill="x", padx=20, pady=10)

        self.btn_step1 = ttk.Button(btn_frame, text="1. Run Email Table Extractor", command=self.run_gas_web)
        self.btn_step1.pack(side="left", fill="x", expand=True, padx=10, pady=12)

        self.btn_step2 = ttk.Button(btn_frame, text="2. Run Local FTP Downloader Now", command=self.start_ftp_thread)
        self.btn_step2.pack(side="left", fill="x", expand=True, padx=10, pady=12)

        # Execution Log Box
        log_frame = ttk.LabelFrame(root, text=" Activity Log ")
        log_frame.pack(fill="both", expand=True, padx=20, pady=(5, 15))

        self.log_area = scrolledtext.ScrolledText(log_frame, height=10, font=("Consolas", 9))
        self.log_area.pack(fill="both", expand=True, padx=8, pady=8)

        self.log("System initialized. Control panel ready.")

    def log(self, text):
        """Thread-safe logging helper."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.root.after(0, self._append_log, f"[{timestamp}] {text}\n")

    def _append_log(self, formatted_text):
        self.log_area.insert(tk.END, formatted_text)
        self.log_area.see(tk.END)

    def run_gas_web(self):
        self.log("--- Triggering Google Apps Script ---")
        def _gas_worker():
            try:
                ctx = ssl.create_default_context()
                ctx.check_hostname = False
                ctx.verify_mode = ssl.CERT_NONE

                req = urllib.request.Request(
                    GAS_URL, 
                    headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                )
                
                with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
                    result_text = response.read().decode('utf-8')
                    self.log(f"Apps Script Output: {result_text}")
                    self.root.after(0, lambda: messagebox.showinfo("Success", f"Google Script Executed!\n\nResponse: {result_text}"))
            except Exception as e:
                self.log(f"Error triggering Google Script: {e}")
                self.root.after(0, lambda: messagebox.showerror("Execution Error", f"Failed to trigger Google Script:\n{e}"))

        threading.Thread(target=_gas_worker, daemon=True).start()

    def start_ftp_thread(self):
        """Launches the FTP downloader in a background thread to prevent UI freezing."""
        if not os.path.exists(PYTHON_FTP_SCRIPT):
            messagebox.showerror("File Error", f"Cannot find script at:\n{PYTHON_FTP_SCRIPT}")
            return

        self.btn_step2.config(state="disabled")
        self.log("--- Starting Manual FTP Pull (Background Task) ---")
        
        threading.Thread(target=self._run_ftp_subprocess, daemon=True).start()

    def _run_ftp_subprocess(self):
        try:
            process = subprocess.Popen(
                ["python", "-u", PYTHON_FTP_SCRIPT],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1
            )
            
            # Read stdout line-by-line as files download
            for line in iter(process.stdout.readline, ''):
                if line:
                    self.log(line.strip())
            process.stdout.close()
            
            process.wait()
            self.log("--- Manual FTP Pull Complete ---")
            self.root.after(0, lambda: messagebox.showinfo("Success", "FTP Download process completed successfully!"))
        except Exception as e:
            self.log(f"Execution Error: {e}")
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.root.after(0, lambda: self.btn_step2.config(state="normal"))

if __name__ == "__main__":
    root = tk.Tk()
    app = WaferControlPanel(root)
    root.mainloop()