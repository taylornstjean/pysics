import bpy
import os
import numpy as np
from pysics.core.models import Particle
import vpython


def setup_scene():

    # remove the old test file is it exists
    try:
        os.remove("test.blend")
    except FileNotFoundError:
        pass

    # Deselect all
    bpy.ops.object.select_all(action='DESELECT')

    # delete the light and default cube
    bpy.data.objects['Cube'].select_set(True)
    bpy.ops.object.delete()

    bpy.data.objects['Light'].select_set(True)
    bpy.ops.object.delete()

    # set camera position and rotation
    c_position = [-100., -100., 0.]
    c_rotation = [1.69, 0., 5.51]

    for i, p in enumerate(c_position):
        bpy.data.objects["Camera"].location[i] = p

    for i, r in enumerate(c_rotation):
        bpy.data.objects["Camera"].rotation_euler[i] = r

    camera = bpy.context.scene.camera
    camera.data.clip_start = 0.1  # Minimum render distance
    camera.data.clip_end = 1000.0  # Maximum render distance

    # set render quality
    bpy.context.scene.render.resolution_x = 2048
    bpy.context.scene.render.resolution_y = 1080

    # set bloom parameters
    bpy.context.scene.use_nodes = True
    tree = bpy.context.scene.node_tree

    # delete default nodes
    for node in tree.nodes:
        tree.nodes.remove(node)

    # create render layers node
    render_layers_node = tree.nodes.new(type="CompositorNodeRLayers")

    # create the glare node for bloom
    glare_node = tree.nodes.new(type="CompositorNodeGlare")
    glare_node.glare_type = 'BLOOM'

    # define some parameters for bloom
    glare_node.mix = -0.9985
    glare_node.threshold = 0.2
    glare_node.size = 9

    # create composite node
    composite_node = tree.nodes.new(type="CompositorNodeComposite")

    # link nodes together
    links = tree.links
    links.new(render_layers_node.outputs[0], glare_node.inputs[0])
    links.new(glare_node.outputs[0], composite_node.inputs[0])

    # set background color
    bpy.data.worlds["World"].node_tree.nodes["Background"].inputs[0].default_value = (0, 0, 0, 1)


def configure_cycles():

    # set renderer
    bpy.data.scenes["Scene"].render.engine = "CYCLES"

    bpy.context.scene.cycles.samples = 64  # Use lower samples (default is 128 or higher)
    bpy.context.scene.cycles.preview_samples = 16  # Reduce viewport samples for faster previews

    bpy.context.scene.cycles.use_denoising = True

    bpy.context.scene.cycles.max_bounces = 4  # Default is often 12
    bpy.context.scene.cycles.glossy_bounces = 2
    bpy.context.scene.cycles.transmission_bounces = 2

    bpy.context.scene.cycles.device = 'GPU'
    bpy.context.preferences.addons['cycles'].preferences.compute_device_type = 'HIP'


def set_star(obj):

    color = [1., 0.8, 0.2, 1.]
    strength = 500.0

    material = bpy.data.materials.new(name="Star")
    obj.data.materials.append(material)

    material.use_nodes = True
    nodes = material.node_tree.nodes

    material_output = nodes.get("Material Output")
    node_emission = nodes.new(type="ShaderNodeEmission")

    node_emission.inputs[0].default_value = color
    nodes["Principled BSDF"].inputs[0].default_value = color
    node_emission.inputs[1].default_value = strength

    links = material.node_tree.links
    links.new(node_emission.outputs[0], material_output.inputs[0])


def run_render(*args, generate=False):

    setup_scene()

    # set the intended fps and total time to run for
    fps = 60
    run_time = 100
    frames = fps * run_time
    time_resolution = 1 / fps

    bpy.context.scene.render.fps = fps
    bpy.data.scenes["Scene"].frame_end = frames

    objects = {}

    # set initial conditions
    bpy.context.scene.frame_set(1)

    for i, obj in enumerate(args):
        bpy.ops.mesh.primitive_ico_sphere_add(
            subdivisions=6, enter_editmode=False, align='WORLD', location=obj.p, scale=(0.5, 0.5, 0.5))

        # name and store reference
        objects[i] = {"blender_ref": bpy.context.active_object, "class_ref": obj}
        objects[i]["blender_ref"].name = f"object.{i}"

        # apply material to object
        set_star(objects[i]["blender_ref"])

    for f in range(frames):

        # set to next frame
        bpy.context.scene.frame_set(f + 2)

        # move each object
        for i, obj in objects.items():

            # perform one interaction
            obj["class_ref"].interact(t_res=time_resolution)

            for j in range(3):
                obj["blender_ref"].location[j] = obj["class_ref"].p[j]

            obj["blender_ref"].keyframe_insert(data_path="location", index=-1)

    # reset to first frame before saving
    bpy.context.scene.frame_set(1)

    bpy.ops.wm.save_as_mainfile(filepath=os.path.abspath("test.blend"))

    if generate:
        render()


def render(cycles=False):

    if cycles:
        configure_cycles()

    bpy.context.scene.render.image_settings.file_format = 'FFMPEG'
    bpy.context.scene.render.ffmpeg.format = 'MPEG4'
    bpy.context.scene.render.ffmpeg.codec = 'H264'
    bpy.context.scene.render.ffmpeg.constant_rate_factor = 'MEDIUM'
    bpy.context.scene.render.filepath = "C:\\Users\\Taylor St Jean\\Documents\\pysics\\output\\render_output.mp4"  # Save relative to the .blend file

    bpy.ops.render.render(animation=True)


def render_3d(cycles=False):

    if cycles:
        configure_cycles()

    bpy.ops.export_scene.gltf(filepath="C:\\Users\\Taylor St Jean\\Documents\\pysics\\output\\render_output.glb", export_animations=True)


