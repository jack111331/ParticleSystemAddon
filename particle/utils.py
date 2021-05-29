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
    SCALE=0.5
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

def create_collection(parent_collection, collection_name):
    new_collection = bpy.data.collections.new(name=collection_name)
    parent_collection.children.link(new_collection)
    return new_collection