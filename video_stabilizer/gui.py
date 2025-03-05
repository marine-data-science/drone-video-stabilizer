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

        self.label = tk.Label(root, text="Select a file or folder:", font=("Arial", 12))
        self.label.pack(pady=10)

        self.select_file_btn = tk.Button(root, text="Select Video", command=self.select_video, width=20)
        self.select_file_btn.pack(pady=5)

        self.select_folder_btn = tk.Button(root, text="Select Folder", command=self.select_folder, width=20)
        self.select_folder_btn.pack(pady=5)

        self.progress_label = tk.Label(root, text="")
        self.progress_label.pack(pady=10)

        self.process_btn = tk.Button(root, text="Start", command=self.start_processing, state=tk.DISABLED, width=20)
        self.process_btn.pack(pady=5)

        self.quit_btn = tk.Button(root, text="Quit", command=root.quit, width=20)
        self.quit_btn.pack(pady=10)

        self.input_path = None
        self.is_folder = False

        self.progress = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
        self.progress.pack(pady=10)

    def select_video(self):
        file_path = filedialog.askopenfilename(filetypes=[("MP4 Files", "*.mp4")])
        if file_path:
            self.input_path = file_path
            self.is_folder = False
            self.progress_label.config(text=f"Selected Video: {os.path.basename(file_path)}")
            self.process_btn.config(state=tk.NORMAL)

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.input_path = folder_path
            self.is_folder = True
            self.progress_label.config(text=f"Selected Folder: {folder_path}")
            self.process_btn.config(state=tk.NORMAL)

    def start_processing(self):
        if not self.input_path:
            messagebox.showerror("Error", "Please select a file or folder first!")
            return

        self.process_btn.config(state=tk.DISABLED)
        self.progress_label.config(text="Processing...")

        # Run processing in a separate thread to keep the GUI responsive
        threading.Thread(target=self.process_videos).start()

    def process_videos(self):
        if self.is_folder:
            videos = [os.path.join(self.input_path, f) for f in os.listdir(self.input_path) if f.lower().endswith(".mp4")]
        else:
            videos = [self.input_path]

        total_videos = len(videos)

        def process_next(index=0):
            if index < total_videos:
                video = videos[index]
                output_path = os.path.join(os.path.dirname(video), f"{os.path.splitext(os.path.basename(video))[0]}_stabilized.mp4")

                self.root.after(0, self.progress_label.config, {"text": f"Processing ({index+1}/{total_videos})"})
                self.root.after(0, self.root.update_idletasks)

                def run_stabilization():
                    try:
                        self.stabilize_video(video, output_path)
                        self.root.after(0, process_next, index + 1)
                    except Exception as e:
                        self.root.after(0, messagebox.showerror, "Error", f"Error with {video}: {str(e)}")

                threading.Thread(target=run_stabilization, daemon=True).start()
            else:
                self.root.after(0, messagebox.showinfo, "Done!", "All videos have been stabilized.")
                self.root.after(0, self.progress_label.config, {"text": "Done!"})
                self.root.after(0, self.process_btn.config, {"state": tk.NORMAL})
                self.root.after(0, self.progress.config, {"value": 0})

        self.root.after(0, process_next)

    def stabilize_video(self, input_path, output_path):
        def on_loop_progress(frame_idx):
            self.progress["value"] = frame_idx
            self.root.update_idletasks()

        def before_loop(total_frames):
            self.progress["maximum"] = total_frames

        self.progress["value"] = 0
        stabilize_video(input_path, output_path, before_loop, on_loop_progress)
