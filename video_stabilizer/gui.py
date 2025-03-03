import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tqdm import tqdm
import threading
from .logic import stabilize_video

class VideoStabilizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Stabilizer")
        self.root.geometry("400x300")

        self.label = tk.Label(root, text="Wähle eine Datei oder einen Ordner:", font=("Arial", 12))
        self.label.pack(pady=10)

        self.select_file_btn = tk.Button(root, text="Video auswählen", command=self.select_video, width=20)
        self.select_file_btn.pack(pady=5)

        self.select_folder_btn = tk.Button(root, text="Ordner auswählen", command=self.select_folder, width=20)
        self.select_folder_btn.pack(pady=5)

        self.progress_label = tk.Label(root, text="")
        self.progress_label.pack(pady=10)

        self.process_btn = tk.Button(root, text="Starten", command=self.start_processing, state=tk.DISABLED, width=20)
        self.process_btn.pack(pady=5)

        self.quit_btn = tk.Button(root, text="Beenden", command=root.quit, width=20)
        self.quit_btn.pack(pady=10)

        self.input_path = None
        self.is_folder = False

        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

    def select_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP4 Dateien", "*.mp4")])
        if file_path:
            self.input_path = file_path
            self.is_folder = False
            self.progress_label.config(text=f"Ausgewähltes Video: {os.path.basename(file_path)}")
            self.process_btn.config(state=tk.NORMAL)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.input_path = folder_path
            self.is_folder = True
            self.progress_label.config(text=f"Ausgewählter Ordner: {folder_path}")
            self.process_btn.config(state=tk.NORMAL)

    def start_processing(self):
        if not self.input_path:
            messagebox.showerror("Fehler", "Bitte zuerst eine Datei oder einen Ordner auswählen!")
            return

        self.process_btn.config(state=tk.DISABLED)
        self.progress_label.config(text="Verarbeitung läuft...")

        # Führe die Verarbeitung in einem separaten Thread aus, um die GUI nicht einzufrieren
        threading.Thread(target=self.process_videos).start()

    def process_videos(self):
        if self.is_folder:
            videos = [os.path.join(self.input_path, f) for f in os.listdir(self.input_path) if f.lower().endswith(".mp4")]
        else:
            videos = [self.input_path]

        for index, video in enumerate(tqdm(videos, desc="Stabilisierung"), start=1):
            self.progress_label.config(text=f"Verarbeitung läuft ({index}/{len(videos)})")
            self.root.update_idletasks()  # GUI aktualisieren, damit das Label sofort sichtbar wird

            filename, ext = os.path.splitext(os.path.basename(video))  # Trennt Namen und Extension
            output_path = os.path.join(os.path.dirname(video), f"{filename}_stabilized{ext}")
            self.stabilize_video(video, output_path)

        messagebox.showinfo("Fertig!", "Alle Videos wurden stabilisiert.")
        self.progress_label.config(text="Fertig!")
        self.process_btn.config(state=tk.NORMAL)
        self.progress["value"] = 0

    def stabilize_video(self, input_path, output_path):
        def on_loop_progress(frame_idx):
            self.progress["value"] = frame_idx
            self.root.update_idletasks()

        def before_loop(total_frames):
            self.progress["maximum"] = total_frames

        self.progress["value"] = 0
        stabilize_video(input_path, output_path, before_loop, on_loop_progress)
