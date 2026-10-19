import math
import os
import sys
from mathutils import Vector

import bpy


ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FONT_PATH = os.path.join(ROOT, "assets", "fonts", "Manrope.ttf")
BLEND_PATH = os.path.join(ROOT, "src", "blender", "ai-tools-2026.blend")


PRODUCTS = [
    ("CHATGPT", 0.16, 0.83, 0.72),
    ("GEMINI", 0.25, 0.52, 1.00),
    ("CLAUDE", 0.95, 0.42, 0.22),
    ("DEEPSEEK", 0.30, 0.62, 1.00),
    ("GROK", 0.82, 0.88, 0.95),
    ("COPILOT", 0.45, 0.68, 1.00),
    ("PERPLEXITY", 0.25, 0.88, 0.78),
]


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for datablocks in (
        bpy.data.materials,
        bpy.data.curves,
        bpy.data.meshes,
        bpy.data.cameras,
        bpy.data.lights,
    ):
        for datablock in list(datablocks):
            if datablock.users == 0:
                datablocks.remove(datablock)


def emission_material(name, color, strength=4.0, metallic=0.15, roughness=0.28):
    material = bpy.data.materials.new(name)
    material.use_nodes = True
    nodes = material.node_tree.nodes
    principled = nodes.get("Principled BSDF")
    principled.inputs["Base Color"].default_value = (*color, 1.0)
    principled.inputs["Metallic"].default_value = metallic
    principled.inputs["Roughness"].default_value = roughness
    principled.inputs["Emission Color"].default_value = (*color, 1.0)
    principled.inputs["Emission Strength"].default_value = strength
    return material


def add_uv_sphere(name, location, radius, material, segments=32, rings=16):
    bpy.ops.mesh.primitive_uv_sphere_add(
        segments=segments,
        ring_count=rings,
        radius=radius,
        location=location,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def add_text(name, body, location, rotation, size, material):
    curve = bpy.data.curves.new(name=f"{name}-curve", type="FONT")
    curve.body = body
    curve.align_x = "CENTER"
    curve.align_y = "CENTER"
    curve.size = size
    curve.extrude = 0.045
    curve.bevel_depth = 0.012
    curve.bevel_resolution = 3
    if os.path.exists(FONT_PATH):
        curve.font = bpy.data.fonts.load(FONT_PATH, check_existing=True)
    obj = bpy.data.objects.new(name, curve)
    obj.location = location
    obj.rotation_euler = rotation
    obj.data.materials.append(material)
    bpy.context.collection.objects.link(obj)
    return obj


def add_ring(name, radius, thickness, rotation, material):
    bpy.ops.mesh.primitive_torus_add(
        major_radius=radius,
        minor_radius=thickness,
        major_segments=96,
        minor_segments=12,
        location=(0, 0, 0),
        rotation=rotation,
    )
    obj = bpy.context.object
    obj.name = name
    obj.data.materials.append(material)
    return obj


def track_camera(camera, target=(0, 0, 0)):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def build():
    clear_scene()

    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1080
    scene.render.resolution_y = 1920
    scene.render.resolution_percentage = 100
    scene.render.fps = 30
    scene.render.image_settings.file_format = "PNG"
    scene.render.image_settings.color_mode = "RGB"
    scene.render.image_settings.color_depth = "8"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "Standard"
    scene.view_settings.look = "None"

    world = scene.world or bpy.data.worlds.new("AI Space")
    scene.world = world
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs["Color"].default_value = (
        0.006,
        0.013,
        0.022,
        1.0,
    )
    world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.12

    cyan = emission_material("Instrument Cyan", (0.08, 0.68, 1.0), 5.0, 0.25, 0.2)
    amber = emission_material("Signal Amber", (1.0, 0.42, 0.10), 5.5, 0.2, 0.22)
    dark_metal = emission_material("Dark Structure", (0.018, 0.035, 0.052), 0.2, 0.78, 0.22)
    white = emission_material("White Type", (0.82, 0.94, 1.0), 2.8, 0.15, 0.28)

    core = add_uv_sphere("Intelligence Core", (0, 0, 0), 1.35, cyan, 64, 32)
    core.scale = (1.0, 1.0, 1.35)

    for index, (name, r, g, b) in enumerate(PRODUCTS):
        angle = index * (2 * math.pi / len(PRODUCTS)) + 0.2
        radius = 6.2 + (index % 2) * 1.35
        z = (index - 3) * 1.25
        location = (
            math.cos(angle) * radius,
            math.sin(angle) * radius,
            z,
        )
        material = emission_material(f"{name} Material", (r, g, b), 5.2, 0.18, 0.2)
        node = add_uv_sphere(f"{name} Node", location, 0.54, material, 40, 20)
        node.scale = (1.0, 1.0, 1.25)
        label_rotation = (0, 0, 0)
        label_location = (
            location[0] * 1.05,
            location[1] * 1.05,
            location[2] + 1.18,
        )
        add_text(
            f"{name} Label",
            name,
            label_location,
            label_rotation,
            0.56 if len(name) < 9 else 0.43,
            material,
        )

    add_ring("Ring A", 8.8, 0.035, (math.pi / 2, 0, 0.18), cyan)
    add_ring("Ring B", 10.2, 0.028, (math.pi / 2, 0, -0.72), amber)
    add_ring("Ring C", 7.4, 0.022, (0.28, 0.15, 0.0), white)

    # Deterministic sparse star field: depth without random motion noise.
    for index in range(90):
        t = (index + 0.5) / 90
        theta = index * 2.3999632297
        y = 1 - 2 * t
        radial = math.sqrt(max(0.0, 1 - y * y))
        distance = 15 + (index % 5) * 1.8
        location = (
            math.cos(theta) * radial * distance,
            math.sin(theta) * radial * distance,
            y * distance,
        )
        star = add_uv_sphere(
            f"Signal Dust {index:03d}",
            location,
            0.035 + (index % 3) * 0.012,
            cyan if index % 5 else amber,
            12,
            8,
        )
        star.scale = (1.0, 1.0, 2.2)

    for location, energy, color in (
        ((7, -8, 10), 2200, (0.15, 0.65, 1.0)),
        ((-9, -4, 3), 1600, (1.0, 0.3, 0.08)),
        ((0, 9, -7), 1100, (0.2, 0.45, 1.0)),
    ):
        bpy.ops.object.light_add(type="AREA", location=location)
        light = bpy.context.object
        light.data.energy = energy
        light.data.color = color
        light.data.shape = "DISK"
        light.data.size = 8.0
        track_camera(light)

    bpy.ops.object.camera_add(location=(0, -32, 14))
    camera = bpy.context.object
    camera.name = "Cinematic Camera"
    camera.data.lens = 47
    camera.data.dof.use_dof = True
    camera.data.dof.focus_object = core
    camera.data.dof.aperture_fstop = 2.8
    scene.camera = camera

    for obj in bpy.data.objects:
        if obj.name.endswith("Label"):
            constraint = obj.constraints.new("TRACK_TO")
            constraint.name = "Face Camera"
            constraint.target = camera
            constraint.track_axis = "TRACK_Z"
            constraint.up_axis = "UP_Y"

    for frame, location, target in (
        (1, (0, -34, 15), (0, 0, 0.8)),
        (90, (-13, -28, 11), (0, 0, 0)),
        (210, (13, -23, 8), (0, 0, 0)),
        (300, (18, -28, 17), (0, 0, 1.2)),
        (420, (0, -38, 23), (0, 0, 0)),
        (540, (-18, -33, 26), (0, 0, 0)),
    ):
        scene.frame_set(frame)
        camera.location = location
        track_camera(camera, target)
        camera.keyframe_insert(data_path="location", frame=frame)
        camera.keyframe_insert(data_path="rotation_euler", frame=frame)

    for obj in bpy.data.objects:
        if obj.name.endswith("Node") or obj.name.endswith("Label"):
            obj.rotation_mode = "XYZ"
            start_rotation = obj.rotation_euler.copy()
            scene.frame_set(1)
            obj.rotation_euler = start_rotation
            obj.keyframe_insert(data_path="rotation_euler", frame=1)
            scene.frame_set(540)
            obj.rotation_euler.z += math.radians(28)
            obj.keyframe_insert(data_path="rotation_euler", frame=540)

    for ring_name, speed in (("Ring A", 0.65), ("Ring B", -0.42), ("Ring C", 0.26)):
        ring = bpy.data.objects[ring_name]
        scene.frame_set(1)
        ring.keyframe_insert(data_path="rotation_euler", frame=1)
        scene.frame_set(540)
        ring.rotation_euler.z += math.pi * speed
        ring.keyframe_insert(data_path="rotation_euler", frame=540)

    scene.frame_start = 1
    scene.frame_end = 540
    bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
    print(f"Saved editable Blender scene: {BLEND_PATH}")


if "--" in sys.argv:
    args = sys.argv[sys.argv.index("--") + 1 :]
else:
    args = []

if "--build" in args:
    build()
