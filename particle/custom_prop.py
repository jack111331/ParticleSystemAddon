import bpy
from mathutils import Vector


def update_particle_prop(self, context):
    ParticleProp.particle_reference.mass = bpy.context.scene.particle_property.init_mass.__getitem__(0)
    getitem_func = bpy.context.scene.particle_property.init_location.__getitem__
    ParticleProp.particle_reference.location = Vector((getitem_func(0), getitem_func(1), getitem_func(2)))
    getitem_func = bpy.context.scene.particle_property.init_velocity.__getitem__
    ParticleProp.particle_reference.velocity = Vector((getitem_func(0), getitem_func(1), getitem_func(2)))


class ParticleProp(bpy.types.PropertyGroup):
    init_location: bpy.props.FloatVectorProperty(size=3, update=update_particle_prop)
    init_velocity: bpy.props.FloatVectorProperty(size=3, update=update_particle_prop)
    init_mass: bpy.props.FloatVectorProperty(size=1, update=update_particle_prop)
    particle_reference = None

def update_constant_force_prop(self, context):
    getitem_func = bpy.context.scene.constant_force_vector.constant_force_vector.__getitem__
    ConstantForceProp.constant_force_reference.force_constant = (getitem_func(0), getitem_func(1), getitem_func(2))

class ConstantForceProp(bpy.types.PropertyGroup):
    constant_force_vector: bpy.props.FloatVectorProperty(size=3, update=update_constant_force_prop)
    constant_force_reference = None

def update_damping_force_prop(self, context):
    DampingForceProp.damping_force_reference.damp_constant = (bpy.context.scene.damping_constant.damping_constant.__getitem__(0), )

class DampingForceProp(bpy.types.PropertyGroup):
    damping_constant: bpy.props.FloatVectorProperty(size=1, update=update_damping_force_prop)
    damping_force_reference = None

def update_spring_force_prop(self, context):
    SpringForceProp.spring_force_reference.spring_constant = (bpy.context.scene.spring_force.spring_constant.__getitem__(0), )
    getitem_func = bpy.context.scene.spring_force.spring_rest_location.__getitem__
    SpringForceProp.spring_force_reference.rest_location = (getitem_func(0), getitem_func(1), getitem_func(2))

class SpringForceProp(bpy.types.PropertyGroup):
    spring_constant: bpy.props.FloatVectorProperty(size=1, update=update_spring_force_prop)
    spring_rest_location: bpy.props.FloatVectorProperty(size=3, update=update_spring_force_prop)
    spring_force_reference = None



def update_angular_constraint_prop(self, context):
    AngularConstraintProp.angular_constraint_reference.pair_particle = bpy.context.scene.angular_constraint.min_angle.__getitem__(0)
    AngularConstraintProp.angular_constraint_reference.min_angle = bpy.context.scene.angular_constraint.min_angle.__getitem__(0)
    AngularConstraintProp.angular_constraint_reference.max_angle = bpy.context.scene.angular_constraint.max_angle.__getitem__(0)
    if AngularConstraintProp.angular_constraint_reference.min_angle >= AngularConstraintProp.angular_constraint_reference.max_angle:
        AngularConstraintProp.angular_constraint_reference.max_angle = AngularConstraintProp.angular_constraint_reference.min_angle
    if AngularConstraintProp.angular_constraint_reference.max_angle <= AngularConstraintProp.angular_constraint_reference.min_angle:
        AngularConstraintProp.angular_constraint_reference.min_angle = AngularConstraintProp.angular_constraint_reference.max_angle

class AngularConstraintProp(bpy.types.PropertyGroup):
    min_angle: bpy.props.FloatVectorProperty(size=1, min=0.0, max=3.14159, update=update_angular_constraint_prop)
    max_angle: bpy.props.FloatVectorProperty(size=1, min=0.0, max=3.14159, update=update_angular_constraint_prop)
    angular_constraint_reference = None