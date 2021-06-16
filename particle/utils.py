import bpy
import bmesh
from mathutils import Vector, Matrix

def getParticleSystem(obj):
    pasy = obj.particle_systems.active
    pamo = None
    for modifier in obj.modifiers:
        if isinstance(modifier, bpy.types.ParticleSystemModifier) and modifier.particle_system == pasy:
            pamo = modifier
            break
    return (pasy, pamo)

def create_sphere(collection, name, position):
    # Create an empty mesh and the object.
    SCALE=1.0
    mesh = bpy.data.meshes.new(name)
    sphere_ob = bpy.data.objects.new(name, mesh)

    # Select the newly created object
    collection.objects.link(sphere_ob)
    bpy.context.view_layer.objects.active = sphere_ob
    sphere_ob.select_set(True)

    # Construct the bmesh sphere and assign it to the blender mesh.
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, diameter=1)
    bm.to_mesh(mesh)
    bm.free()

    bpy.ops.object.modifier_add(type='SUBSURF')
    bpy.ops.object.shade_smooth()


    sphere_ob.location = position
    sphere_ob.scale = Vector((SCALE, SCALE, SCALE))
    return sphere_ob

def create_plane(collection, name, position):
    # Create an empty mesh and the object.
    SCALE=4.0
    mesh = bpy.data.meshes.new(name)
    plane_ob = bpy.data.objects.new(name, mesh)

    # Select the newly created object
    collection.objects.link(plane_ob)
    bpy.context.view_layer.objects.active = plane_ob
    plane_ob.select_set(True)

    # Construct the bmesh plane and assign it to the blender mesh.
    bm = bmesh.new()
    bm.verts.new((SCALE, SCALE, 0))
    bm.verts.new((SCALE, -SCALE, 0))
    bm.verts.new((-SCALE, SCALE, 0))
    bm.verts.new((-SCALE, -SCALE, 0))
    bmesh.ops.contextual_create(bm, geom=bm.verts)
    bm.to_mesh(mesh)
    bm.free()

    plane_ob.location = position
    return plane_ob

def create_connect_line(collection, ob_1, ob_2):
    mesh = bpy.data.meshes.new('connector')

    bm = bmesh.new()
    v1 = bm.verts.new(ob_1.location)
    v2 = bm.verts.new(ob_2.location)
    e = bm.edges.new([v1, v2])

    bm.to_mesh(mesh)
    obj = bpy.data.objects.new('connector', mesh)
    collection.objects.link(obj)

    for i, target_obj in enumerate([ob_1, ob_2]):
        bpy.ops.object.select_all(action='DESELECT')
        target_obj.select_set(True)
        obj.select_set(True)
        bpy.context.view_layer.objects.active = obj  # Set connector as active

        # Select vertex
        bpy.ops.object.mode_set(mode='OBJECT')
        obj.data.vertices[i].select = True
        bpy.ops.object.mode_set(mode='EDIT')

        bpy.ops.object.hook_add_selob()  # Hook to cylinder

        bpy.ops.object.mode_set(mode='OBJECT')
        obj.data.vertices[i].select = False

    mesh = obj.modifiers.new('Skin', 'SKIN')

    ## New bit starts here
    mesh.use_smooth_shade = True

    mesh = obj.modifiers.new('Subsurf', 'SUBSURF')
    mesh.levels = 2
    mesh.render_levels = 2

    ## End of new bit
    bpy.ops.object.select_all(action='DESELECT')

def create_collection(parent_collection, collection_name):
    new_collection = bpy.data.collections.new(name=collection_name)
    parent_collection.children.link(new_collection)
    return new_collection