import argparse
import os
from rich import print
from tqdm import tqdm
from .logic import stabilize_video

def command_line():
    parser = argparse.ArgumentParser(description="CLI to stabilize stationary videos.")
    parser.add_argument("input", type=str, help="Path to Input Video(.mp4)")
    parser.add_argument("-o", "--output", type=str, help="Output File (optional)")
    parser.add_argument("--skip-outlier-frames", action="store_true", help="Skip frames which could not be stabilized (optional)")

    args = parser.parse_args()
    input_path = args.input

    if not input_path.lower().endswith(".mp4"):
        print("[red]Error: Input file needs to be an mp4 file.[/red]")
        return

    output_path = args.output if args.output else f"{os.path.splitext(input_path)[0]}_stabilized.mp4"

    progress_bar = None

    def before_loop(total_frames: int):
        nonlocal progress_bar
        progress_bar = tqdm(total=total_frames, desc="Stabilisierung", unit="frame")

    def on_loop_progress(_: int):
        if progress_bar:
            progress_bar.update(1)

    (invalid_frames) =stabilize_video(input_path, output_path, before_loop, on_loop_progress, args.skip_outlier_frames)

    if progress_bar:
        progress_bar.close()

    if args.skip_outlier_frames and not invalid_frames == 0:
        print("[yellow]The flag [bold]--skip-outlier-frames[/bold] was used[/yellow]")
        print(f"[yellow]   Number of outlier frames: [/yellow][bold red]{invalid_frames}[/bold red]")

    print(f"[green]Stabilized video saved at: [bold]{output_path}[/bold][/green]")
