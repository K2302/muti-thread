import threading
import requests
import tkinter as tk
from tkinter import ttk

# --- Model ---
class DownloaderModel:
    def download_file(self, url, filename, progress_callback, status_callback):
        try:
            response = requests.get(url, stream=True)
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            with open(filename, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total_size:
                            percent = downloaded / total_size * 100
                            progress_callback(percent)
            status_callback("✅ Completed")
        except Exception as e:
            status_callback(f"❌ Error: {e}")

# --- View (GUI) ---
class DownloaderView(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🚀 Multi File Downloader")
        self.geometry("600x400")
        self.resizable(False, False)

        self.url_entries = []
        self.filename_entries = []
        self.progress_bars = []
        self.status_labels = []

        self.canvas = tk.Canvas(self)
        self.scrollbar = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        self.scrollbar.pack(side="right", fill="y")

        self.add_input_row()
        self.add_row_button = tk.Button(self, text="Add More Files", command=self.add_input_row)
        self.add_row_button.pack(pady=5)
        self.start_button = tk.Button(self, text="Start Download", command=self.on_start_click)
        self.start_button.pack(pady=5)

        self.controller = None

    def add_input_row(self):
        row = len(self.url_entries)
        url_entry = tk.Entry(self.scrollable_frame, width=60)
        url_entry.grid(row=row, column=0, padx=5, pady=5)
        filename_entry = tk.Entry(self.scrollable_frame, width=25)
        filename_entry.grid(row=row, column=1, padx=5, pady=5)

        progress = ttk.Progressbar(self.scrollable_frame, orient="horizontal", length=300, mode="determinate")
        progress.grid(row=row, column=2, padx=5)
        status = tk.Label(self.scrollable_frame, text="", fg="blue")
        status.grid(row=row, column=3, padx=5)

        self.url_entries.append(url_entry)
        self.filename_entries.append(filename_entry)
        self.progress_bars.append(progress)
        self.status_labels.append(status)

    def on_start_click(self):
        if self.controller:
            for i in range(len(self.url_entries)):
                url = self.url_entries[i].get()
                filename = self.filename_entries[i].get()
                progress_bar = self.progress_bars[i]
                status_label = self.status_labels[i]
                if url.strip() and filename.strip():
                    self.controller.start_individual_download(url, filename, progress_bar, status_label)

# --- Controller ---
class DownloaderController:
    def __init__(self, view, model):
        self.view = view
        self.model = model
        self.view.controller = self

    def start_individual_download(self, url, filename, progress_bar, status_label):
        def update_progress(percent):
            progress_bar["value"] = percent

        def update_status(msg):
            status_label.config(text=msg)

        thread = threading.Thread(
            target=self.model.download_file,
            args=(url, filename, update_progress, update_status)
        )
        thread.start()

# --- Main ---
if __name__ == "__main__":
    model = DownloaderModel()
    view = DownloaderView()
    controller = DownloaderController(view, model)
    view.mainloop()
