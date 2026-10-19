#!/usr/bin/env python3
"""Refresh rendered frames for a Manim scene and optionally generate a contact sheet."""

import argparse
import subprocess
import sys
import time
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Delete old frames, re-render a Manim scene, and optionally create a contact sheet."
    )
    parser.add_argument(
        "file_path",
        help="Path to the Python file containing the scene (e.g., foo.py)",
    )
    parser.add_argument(
        "scene_name",
        help="Name of the Scene class to render",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=2,
        help="Frames per second for rendering (default: 2)",
    )
    parser.add_argument(
        "--contact-sheet",
        action="store_true",
        help="Generate a contact sheet after rendering",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()

    file_path = Path(args.file_path)
    scene_name = args.scene_name
    fps = args.fps
    make_contact_sheet = args.contact_sheet

    if not file_path.exists():
        print(f"Error: File not found: {file_path}", file=sys.stderr)
        return 1

    base_name = file_path.stem
    image_dir = Path("media") / "images" / base_name

    # Delete old frames
    if image_dir.exists():
        for png_file in image_dir.glob("*.png"):
            png_file.unlink()

    # Render frames
    print(f"Rendering {scene_name} from {file_path} at {fps} FPS...")
    start_time = time.time()

    try:
        subprocess.run(
            [
                "manim",
                "-ql",
                f"--fps",
                str(fps),
                "--format=png",
                "--silent",
                str(file_path),
                scene_name,
            ],
            check=True,
            capture_output=False,
        )
    except subprocess.CalledProcessError as e:
        print(f"Error: Manim rendering failed with exit code {e.returncode}", file=sys.stderr)
        return 1

    elapsed = time.time() - start_time

    # Count frames
    frame_count = 0
    frame_files = []
    if image_dir.exists():
        frame_files = sorted(image_dir.glob("*.png"))
        frame_count = len(frame_files)

    print(f"Rendered {frame_count} frames in {elapsed:.1f}s at {fps} FPS")
    if frame_files:
        first_frame = frame_files[0].name
        last_frame = frame_files[-1].name
        print(f"Frame images: {image_dir.resolve()}/{first_frame} to {last_frame}")

    # Generate contact sheet if requested
    if make_contact_sheet:
        script_dir = Path(__file__).parent
        contact_script = script_dir / "make_contact_sheet.py"
        try:
            subprocess.run(
                [
                    "python3",
                    str(contact_script),
                    str(image_dir),
                    "--scene-name",
                    scene_name,
                    "--fps",
                    str(fps),
                ],
                check=True,
            )
        except subprocess.CalledProcessError as e:
            print(f"Error: Contact sheet generation failed with exit code {e.returncode}", file=sys.stderr)
            return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
