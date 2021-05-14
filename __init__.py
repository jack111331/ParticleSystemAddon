import bpy
from .particle import apply_force
from .particle import particle_system
from .particle import solver
from bpy.props import BoolProperty, EnumProperty
from mathutils import Vector, Matrix
import subprocess
import os


# Install dependency in blender environment
def check_deps(deps_list):
    py_exec = bpy.app.binary_path_python
    for deps in deps_list:
        if not os.path.exists(os.path.join(str(py_exec)[:-14] + 'lib', deps)):
            print('Installing dependency')
            # ensure pip is installed
            subprocess.call([str(py_exec), "-m", "ensurepip", "--user"])
            # update pip
            subprocess.call([str(py_exec), "-m", "pip", "install", "--upgrade", "pip"])
            # install packages
            subprocess.call([str(py_exec), "-m", "pip", "install", f"--target={str(py_exec)[:-14]}" + "lib", deps])


check_deps(deps_list=["scipy", "numpy"])

bl_info = {
    "name": "Particle Simulation Addon",
    "author": "Edge",
    "version": (1, 0, 0),
    "blender": (2, 83, 5),
    "description": "particle simulation",
    "warning": "",
    "wiki_url": "",
    "support": 'TESTING',
    "category": "Particle",
}

class DeleteParticleSystemOperator(bpy.types.Operator):
    bl_idname = "delete_system.particle"
    bl_label = "delete current custom particle system"
    bl_description = "delete current custom particle system"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        p_system.delete_instance()
        current_collection = bpy.data.collections.get("Custom Particle System")
        if current_collection != None:
            bpy.ops.object.select_all(action='DESELECT')
            for ob in current_collection.objects:
                ob.select_set(True)
                bpy.ops.object.delete()
            bpy.data.collections.remove(current_collection)

        return {'FINISHED'}


class ApplyConstantForceOperator(bpy.types.Operator):
    bl_idname = "apply_constant_force.particle"
    bl_label = "apply constant force on particle system"
    bl_description = "select object and apply constant force on it"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        constant_force_vector = Vector(context.scene.constant_force_vector)
        p_system.add_force(apply_force.ConstantForce(constant_force_vector))
        return {'FINISHED'}

class ApplyDampingForceOperator(bpy.types.Operator):
    bl_idname = "apply_damping_force.particle"
    bl_label = "apply damping force on particle system"
    bl_description = "select object and apply damping force on it"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        damping_constant = context.scene.damping_constant
        p_system.add_force(apply_force.DampingForce(damping_constant))
        return {'FINISHED'}

class ApplySpringForceOperator(bpy.types.Operator):
    bl_idname = "apply_spring_force.particle"
    bl_label = "apply spring force on particle system"
    bl_description = "select object and apply spring force on it"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        spring_constant = context.scene.spring_constant
        rest_location = Vector(context.scene.spring_rest_location)
        p_system.add_force(apply_force.SpringForce(spring_constant, rest_location))
        return {'FINISHED'}

class CalculateFrameOperator(bpy.types.Operator):
    bl_idname = "particle.calculate_frame"
    bl_label = "Calculate frame on blender particle system"
    bl_description = "Calculate frame on blender particle system"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        p_system.update_to_object(context, calculate_frame=True)
        return {'FINISHED'}

class AddParticleOperator(bpy.types.Operator):
    bl_idname = "add.particle"
    bl_label = "Add particle to custom particle system"
    bl_description = "add particle custom particle system"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        if len(p_system.particle_list) == 0:
            p_system.add_particle()
        else:
            latest_location = p_system.particle_list[-1].location
            p_system.add_particle(latest_location + Vector((1.0, 0.0, 0.0)))
        p_system = particle_system.ParticleSystem.get_instance()
        p_system.update_to_object(context)
        return {'FINISHED'}

class RemoveParticleOperator(bpy.types.Operator):
    bl_idname = "remove.particle"
    bl_label = "Remove particle to custom particle system"
    bl_description = "remove particle custom particle system"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        p_system.update_to_object(context, calculate_frame=True)
        return {'FINISHED'}

class ApplySolverOperator(bpy.types.Operator):
    bl_idname = "apply.solver"
    bl_label = "Apply solver to custom particle system"
    bl_description = "apply solver custom particle system"


    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        solver_name = context.scene.solver_name
        print(solver_name)
        if solver_name == "FOREULER":
            p_system.solver = solver.ForwardEulerSolver()
        elif solver_name == "2RK":
            p_system.solver = solver.SecondOrderRKSolver()
        elif solver_name == "4RK":
            p_system.solver = solver.FourthOrderRKSolver()
        elif solver_name == "BACKEULER":
            p_system.solver = solver.BackwardEulerSolver()
        return {'FINISHED'}

class ParticleSimulationPanel(bpy.types.Panel):
    bl_idname = "PARTICLE_PT_SIMULATION"
    bl_label = "particle simulation panel"
    bl_category = "Particle System"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        # scene = context.scene

        row = layout.row()
        row.prop(context.scene, "solver_name")
        row.operator('apply.solver', text="apply solver")
        row = layout.row()
        row.operator('delete_system.particle', text="delete particle system")
        row = layout.row()
        row.prop(context.scene, "modify_particle_location", text="Realtime modify particle location")
        row = layout.row()
        row.prop(context.scene, "constant_force_vector", text="Constant force")
        row.operator('apply_constant_force.particle', text="apply constant force")
        row = layout.row()
        row.prop(context.scene, "damping_constant", text="Damping constant")
        row.operator('apply_damping_force.particle', text="apply damping force")
        row = layout.row()
        row.prop(context.scene, "spring_constant", text="Spring constant")
        row.prop(context.scene, "spring_rest_location", text="Spring rest location")
        row.operator('apply_spring_force.particle', text="apply spring force")
        row = layout.row()
        row.operator('particle.calculate_frame', text="calculate frame")
        row = layout.row()
        row.operator('add.particle', text="add particle")
        row.operator('remove.particle', text="remove particle")

        # TODO use a variable force apply panel
        layout.row().separator()

        p_system = particle_system.ParticleSystem.get_instance()
        for force in p_system.force_list:
            force.draw(context, layout)


def solver_item_callback(self, context):
    return (
        ('FOREULER', 'Forward Euler', "Forward euler solver"),
        ('2RK', '2nd order RK', "2nd order runge kutta solver"),
        ('4RK', '4th order RK', "4th order runge kutta solver"),
        ('BACKEULER', 'Backward Euler', "Backward euler solver"),
    )

def obj_location_callback(ob):
    # Do something here
    print('Object "{}" changed its location to: {}: '.format(
        ob.name, ob.location)
    )

def modify_particle_update(self, context):
    print("modify")
    if context.scene.modify_particle_location == True:
        # p_system = particle_system.ParticleSystem.get_instance()
        # for i in range(len(p_system.particle_list)):
        #     object = context.scene.objects.get(str(i))
        #     subscribe_to = object.path_resolve("location", False)
        #     bpy.msgbus.subscribe_rna(
        #         key=subscribe_to,
        #         # owner of msgbus subcribe (for clearing later)
        #         owner=object,
        #         # Args passed to callback function (tuple)
        #         args=(object,),
        #         # Callback function for property update
        #         notify=obj_location_callback,
        #     )
        pass
    else:
        pass
        # TODO
        # p_system = particle_system.ParticleSystem.get_instance()
        # for i in range(len(p_system.particle_list)):
        #     object = context.scene.objects.get(str(i))
        #     subscribe_to = object.path_resolve("location", False)

def register():
    bpy.utils.register_class(DeleteParticleSystemOperator)
    bpy.utils.register_class(ParticleSimulationPanel)
    bpy.utils.register_class(ApplyConstantForceOperator)
    bpy.utils.register_class(ApplyDampingForceOperator)
    bpy.utils.register_class(ApplySpringForceOperator)
    bpy.utils.register_class(CalculateFrameOperator)
    bpy.utils.register_class(AddParticleOperator)
    bpy.utils.register_class(RemoveParticleOperator)
    bpy.utils.register_class(ApplySolverOperator)

    bpy.types.Scene.modify_particle_location = BoolProperty(name="modify_particle_location", update=modify_particle_update)
    bpy.types.Scene.solver_name = bpy.props.EnumProperty(name="solver_name", items=solver_item_callback)
    bpy.types.Scene.constant_force_vector = bpy.props.FloatVectorProperty(size=3)
    bpy.types.Scene.damping_constant = bpy.props.FloatProperty(name="damping_constant")
    bpy.types.Scene.spring_constant = bpy.props.FloatProperty(name="spring_constant")
    bpy.types.Scene.spring_rest_location = bpy.props.FloatVectorProperty(size=3)


def unregister():
    bpy.utils.unregister_class(DeleteParticleSystemOperator)
    bpy.utils.unregister_class(ParticleSimulationPanel)
    bpy.utils.unregister_class(ApplyConstantForceOperator)
    bpy.utils.unregister_class(ApplyDampingForceOperator)
    bpy.utils.unregister_class(ApplySpringForceOperator)
    bpy.utils.unregister_class(CalculateFrameOperator)
    bpy.utils.unregister_class(AddParticleOperator)
    bpy.utils.unregister_class(RemoveParticleOperator)
    bpy.utils.unregister_class(ApplySolverOperator)


if __name__ == "__main__":
    register()
