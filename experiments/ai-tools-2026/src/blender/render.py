import os

import bpy


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
OUTPUT_DIR = os.path.join(ROOT, "assets", "blender")


def render_range(start, end, directory):
    scene = bpy.context.scene
    scene.frame_start = start
    scene.frame_end = end
    scene.render.filepath = os.path.join(OUTPUT_DIR, directory, "frame-")
    bpy.ops.render.render(animation=True)


os.makedirs(OUTPUT_DIR, exist_ok=True)
render_range(1, 210, "opening-frames")
render_range(301, 540, "finale-frames")
print("Rendered Blender opening and finale frame plates.")
