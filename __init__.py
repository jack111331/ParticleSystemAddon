import bpy
from .particle import apply_force
from .particle import particle_system
from .particle import solver
from .particle import custom_prop
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
        # p_system.add_force(apply_force.ConstantForce(context.scene.constant_force_vector))
        p_system.add_force(apply_force.ConstantForce())
        return {'FINISHED'}

class ApplyDampingForceOperator(bpy.types.Operator):
    bl_idname = "apply_damping_force.particle"
    bl_label = "apply damping force on particle system"
    bl_description = "select object and apply damping force on it"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        p_system.add_force(apply_force.DampingForce())
        return {'FINISHED'}

class ApplySpringForceOperator(bpy.types.Operator):
    bl_idname = "apply_spring_force.particle"
    bl_label = "apply spring force on particle system"
    bl_description = "select object and apply spring force on it"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        p_system.add_force(apply_force.SpringForce())
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
        if solver_name == "FOREULER":
            p_system.solver = solver.ForwardEulerSolver()
        elif solver_name == "2RK":
            p_system.solver = solver.SecondOrderRKSolver()
        elif solver_name == "4RK":
            p_system.solver = solver.FourthOrderRKSolver()
        elif solver_name == "BACKEULER":
            p_system.solver = solver.BackwardEulerSolver()
        return {'FINISHED'}

class MassSpringSystemOperator(bpy.types.Operator):
    bl_idname = "particle_system.mass_spring_system"
    bl_label = "Create mass spring system"
    bl_description = "create mass spring system"

    def execute(self, context):
        mass_spring_system = particle_system.MassSpringSystem()
        return {'FINISHED'}

class ClothMassSpringSystemOperator(bpy.types.Operator):
    bl_idname = "particle_system.cloth_mass_spring_system"
    bl_label = "Create cloth mass spring system"
    bl_description = "create cloth mass spring system"

    def execute(self, context):
        mass_spring_system = particle_system.MassSpringSystem(advance=True)
        return {'FINISHED'}

class RemoveForceOperator(bpy.types.Operator):
    bl_idname = "force.remove"
    bl_label = "Remove force"
    bl_description = "remove force"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        force_idx = int(context.scene.force_name)
        p_system.force_list.pop(force_idx)
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
        row.operator('apply_constant_force.particle', text="apply constant force")
        row = layout.row()
        row.operator('apply_damping_force.particle', text="apply damping force")
        row = layout.row()
        row.operator('apply_spring_force.particle', text="apply spring force")
        row = layout.row()
        row.operator('particle.calculate_frame', text="calculate frame")
        row = layout.row()
        row.operator('add.particle', text="add particle")
        row.operator('remove.particle', text="remove particle")
        row = layout.row()
        row.operator('particle_system.mass_spring_system', text="mass spring system")
        row.operator('particle_system.cloth_mass_spring_system', text="cloth system")

        row = layout.row()
        row.separator()
        row.prop(context.scene, 'force_name', text="force list")
        if context.scene.force_name != "None":
            p_system = particle_system.ParticleSystem.get_instance()
            force_idx = int(context.scene.force_name)
            p_system.force_list[force_idx].draw(context, layout)
            row.operator('force.remove', text="remove current force")

def force_item_callback(self, context):
    p_system = particle_system.ParticleSystem.get_instance()
    enum_prop_list = []
    for i, force in enumerate(p_system.force_list):
        enum_prop_list.append((str(i), str(i) + " " + type(force).__name__, str(i) + " " + type(force).__name__))
    if len(enum_prop_list) == 0:
        enum_prop_list.append(("None", "None", "None"))
    return enum_prop_list

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
    bpy.utils.register_class(MassSpringSystemOperator)
    bpy.utils.register_class(RemoveForceOperator)
    bpy.utils.register_class(ClothMassSpringSystemOperator)

    bpy.utils.register_class(custom_prop.ConstantForceProp)
    bpy.utils.register_class(custom_prop.DampingForceProp)
    bpy.utils.register_class(custom_prop.SpringForceProp)

    bpy.types.Scene.modify_particle_location = BoolProperty(name="modify_particle_location", update=modify_particle_update)
    bpy.types.Scene.solver_name = bpy.props.EnumProperty(name="solver_name", items=solver_item_callback)
    bpy.types.Scene.constant_force_vector = bpy.props.PointerProperty(type=custom_prop.ConstantForceProp)
    bpy.types.Scene.damping_constant = bpy.props.PointerProperty(type=custom_prop.DampingForceProp)
    bpy.types.Scene.spring_force = bpy.props.PointerProperty(type=custom_prop.SpringForceProp)
    bpy.types.Scene.force_name = bpy.props.EnumProperty(name="force_name", items=force_item_callback)

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
    bpy.utils.unregister_class(MassSpringSystemOperator)
    bpy.utils.unregister_class(RemoveForceOperator)
    bpy.utils.unregister_class(ClothMassSpringSystemOperator)

    bpy.utils.unregister_class(custom_prop.ConstantForceProp)
    bpy.utils.unregister_class(custom_prop.DampingForceProp)
    bpy.utils.unregister_class(custom_prop.SpringForceProp)



if __name__ == "__main__":
    register()
