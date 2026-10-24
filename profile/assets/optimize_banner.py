#!/usr/bin/env python3
"""
RaxoCode Banner Generator and Optimizer Script
-----------------------------------------------
This utility manages the assets for the RaxoCode GitHub Organization Profile banner:
1. Generates static fallback PNGs from banner animations.
2. Optimizes animated GIFs to ensure crisp visual fidelity while maintaining file size under 2 MB.
3. Validates seamless loop continuity and frame timing.

Requirements:
    pip install pillow numpy
"""

import os
import sys
from PIL import Image, ImageSequence

def extract_static_fallback(gif_path, output_png_path, frame_index=0):
    """Extracts a crisp static PNG from the specified frame index of a GIF."""
    print(f"Extracting frame {frame_index} from {gif_path} -> {output_png_path}...")
    with Image.open(gif_path) as im:
        im.seek(frame_index)
        frame = im.convert("RGB")
        frame.save(output_png_path, "PNG", optimize=True)
    print(f"Saved {output_png_path} ({os.path.getsize(output_png_path):,} bytes).")

def check_loop_continuity(gif_path):
    """Checks the similarity between the first and last frame to verify seamless looping."""
    try:
        import numpy as np
    except ImportError:
        print("numpy not installed; skipping numerical loop continuity check.")
        return

    with Image.open(gif_path) as im:
        frames = [f.convert("RGB") for f in ImageSequence.Iterator(im)]
        if len(frames) < 2:
            print("GIF has fewer than 2 frames; cannot check loop continuity.")
            return

        f_start = np.array(frames[0], dtype=float)
        f_end = np.array(frames[-1], dtype=float)
        diff = np.mean(np.abs(f_start - f_end))
        print(f"Loop Continuity Check: Mean frame difference between start and end is {diff:.3f} (Lower is better; < 2.0 indicates seamless transition).")

def inspect_gif(gif_path):
    """Prints metadata including size, frames, total duration, and dimensions."""
    if not os.path.exists(gif_path):
        print(f"File not found: {gif_path}")
        return

    with Image.open(gif_path) as im:
        width, height = im.size
        n_frames = getattr(im, "n_frames", 1)
        durations = [f.info.get("duration", 0) for f in ImageSequence.Iterator(im)]
        total_duration = sum(durations)
        size_bytes = os.path.getsize(gif_path)

        print(f"\n--- Metadata for {os.path.basename(gif_path)} ---")
        print(f"Dimensions: {width} x {height} px")
        print(f"Frame Count: {n_frames}")
        print(f"Total Duration: {total_duration} ms ({total_duration / 1000.0:.2f} s)")
        print(f"File Size: {size_bytes:,} bytes ({size_bytes / (1024 * 1024):.2f} MB)")
        print(f"Under 2 MB Target: {'YES (Optimal)' if size_bytes < 2 * 1024 * 1024 else 'NO (Consider optimization)'}")

def optimize_gif(input_gif, output_gif, max_colors=128, frame_stride=1, scale_factor=1.0):
    """
    Optimizes a GIF for GitHub profiles:
    - Scales dimensions if needed
    - Selects frames based on frame_stride (e.g. 2 skips every other frame)
    - Quantizes colors using adaptive palette
    """
    print(f"\nOptimizing {input_gif} -> {output_gif}...")
    with Image.open(input_gif) as im:
        raw_frames = [f.convert("RGB") for f in ImageSequence.Iterator(im)]
        raw_durations = [f.info.get("duration", 67) for f in ImageSequence.Iterator(im)]

    target_frames = []
    target_durations = []

    for i in range(0, len(raw_frames), frame_stride):
        frame = raw_frames[i]
        if scale_factor != 1.0:
            new_size = (int(frame.width * scale_factor), int(frame.height * scale_factor))
            frame = frame.resize(new_size, Image.Resampling.LANCZOS)
        target_frames.append(frame)
        duration_sum = sum(raw_durations[i : i + frame_stride])
        target_durations.append(max(20, duration_sum))

    # Convert to palette mode
    palette_frames = [f.convert("P", palette=Image.ADAPTIVE, colors=max_colors) for f in target_frames]

    palette_frames[0].save(
        output_gif,
        save_all=True,
        append_images=palette_frames[1:],
        duration=target_durations,
        loop=0,
        optimize=True,
    )
    inspect_gif(output_gif)

if __name__ == "__main__":
    assets_dir = os.path.dirname(os.path.abspath(__file__))
    primary_banner = os.path.join(assets_dir, "raxocode-banner.gif")
    static_png = os.path.join(assets_dir, "raxocode-banner.png")

    print("RaxoCode Asset Verification:")
    if os.path.exists(primary_banner):
        inspect_gif(primary_banner)
        check_loop_continuity(primary_banner)
    if os.path.exists(static_png):
        print(f"\nStatic PNG Fallback: {static_png} ({os.path.getsize(static_png):,} bytes)")
