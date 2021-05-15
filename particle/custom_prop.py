import bpy

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