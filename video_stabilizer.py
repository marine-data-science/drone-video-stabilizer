import cv2
import numpy as np
import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tqdm import tqdm
import threading

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
            videos = [os.path.join(self.input_path, f) for f in os.listdir(self.input_path) if f.endswith(".mp4")]
        else:
            videos = [self.input_path]

        for video in tqdm(videos, desc="Stabilisierung"):
            output_path = os.path.join(os.path.dirname(video), "stabilized_" + os.path.basename(video))
            self.stabilize_video(video, output_path)

        messagebox.showinfo("Fertig!", "Alle Videos wurden stabilisiert.")
        self.progress_label.config(text="Fertig!")
        self.process_btn.config(state=tk.NORMAL)

    def stabilize_video(self, input_path, output_path):
        cap = cv2.VideoCapture(input_path)
        fps = cap.get(cv2.CAP_PROP_FPS)
        w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))  # Anzahl der Frames für Fortschritt

        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

        ret, ref_frame = cap.read()
        if not ret:
            print("Fehler beim Lesen des Videos.")
            return

        ref_gray = cv2.cvtColor(ref_frame, cv2.COLOR_BGR2GRAY)
        orb = cv2.ORB_create(nfeatures=500)
        kp_ref, des_ref = orb.detectAndCompute(ref_gray, None)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

        frame_idx = 1
        self.progress["value"] = 0
        self.progress["maximum"] = total_frames  # Fortschrittsanzeige auf Gesamtzahl der Frames setzen

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            kp_cur, des_cur = orb.detectAndCompute(gray, None)

            matches = bf.knnMatch(des_ref, des_cur, k=2)
            good_matches = [m for m, n in matches if m.distance < 0.7 * n.distance]

            if len(good_matches) >= 4:
                ref_pts = np.float32([kp_ref[m.queryIdx].pt for m in good_matches])
                cur_pts = np.float32([kp_cur[m.trainIdx].pt for m in good_matches])
                H, mask = cv2.findHomography(cur_pts, ref_pts, cv2.RANSAC)
                stabilized_frame = cv2.warpPerspective(frame, H, (w, h))
                out.write(stabilized_frame)
            else:
                out.write(frame)

            frame_idx += 1
            self.progress["value"] = frame_idx  # Fortschritt aktualisieren
            self.root.update_idletasks()  # GUI aktualisieren

        cap.release()
        out.release()

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoStabilizerApp(root)
    root.mainloop()
