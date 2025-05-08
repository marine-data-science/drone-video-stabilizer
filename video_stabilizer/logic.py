import cv2
import numpy as np
from typing import Callable
from rich import print
import os

def stabilize_video(
    input_path: os.PathLike,
    output_path: os.PathLike,
    before_loop: Callable[[int], None],
    on_loop_progress: Callable[[int], None],
    skip_outlier_frames: bool = False
) -> (int):
    cap = cv2.VideoCapture(input_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, fps, (w, h))

    ret, ref_frame = cap.read()
    if not ret:
        print("[red]Error reading the video file.[/red]")
        return

    ref_gray = cv2.cvtColor(ref_frame, cv2.COLOR_BGR2GRAY)
    orb = cv2.ORB_create(nfeatures=500)
    kp_ref, des_ref = orb.detectAndCompute(ref_gray, None)
    bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)

    frame_idx = 1
    invalid_frames = 0
    before_loop(total_frames)

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
            try:
                stabilized_frame = cv2.warpPerspective(frame, H, (w, h))
                out.write(stabilized_frame)
            except Exception as ex:
                if skip_outlier_frames:
                    invalid_frames +=1
                else:
                    print("[red]An error occured. Possibly the video was not stationary enough.\nYou can try the flag [bold]--skip-outlier-frames[/bold] and see if the result is useful.[/red]")
                    raise ex
        else:
            out.write(frame)

        frame_idx += 1
        on_loop_progress(frame_idx)

    cap.release()
    out.release()

    return (invalid_frames)
