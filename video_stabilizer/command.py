import argparse
import os
from tqdm import tqdm
from .logic import stabilize_video

def command_line():
    parser = argparse.ArgumentParser(description="CLI zum Stabilisieren von Videos.")
    parser.add_argument("input", type=str, help="Pfad zum Eingabevideo (.mp4)")
    parser.add_argument("-o", "--output", type=str, help="Pfad zum Ausgabevideo (optional)")

    args = parser.parse_args()
    input_path = args.input

    if not input_path.lower().endswith(".mp4"):
        print("Fehler: Die Eingabedatei muss eine .mp4 Datei sein.")
        return

    output_path = args.output if args.output else f"{os.path.splitext(input_path)[0]}_stabilized.mp4"

    progress_bar = None

    def before_loop(total_frames: int):
        nonlocal progress_bar
        progress_bar = tqdm(total=total_frames, desc="Stabilisierung", unit="frame")

    def on_loop_progress(_: int):
        if progress_bar:
            progress_bar.update(1)

    stabilize_video(input_path, output_path, before_loop, on_loop_progress)

    if progress_bar:
        progress_bar.close()
    print(f"Video stabilisiert und gespeichert unter: {output_path}")
