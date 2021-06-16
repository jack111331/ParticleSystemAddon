import bpy
from .particle import apply_force
from .particle import particle_system
from .particle import solver
from .particle import custom_prop
from .particle import utils
from .particle import constraint
from .particle import collision
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
        spring_force = apply_force.SpringForce()
        p_system.add_force(spring_force)
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
            p_system.add_particle(latest_location + Vector((2.0, 0.0, 0.0)))
        p_system = particle_system.ParticleSystem.get_instance()
        p_system.update_to_object(context)
        return {'FINISHED'}

class RemoveParticleOperator(bpy.types.Operator):
    bl_idname = "remove.particle"
    bl_label = "Remove particle to custom particle system"
    bl_description = "remove particle custom particle system"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        p_system.remove_particle(int(context.scene.select_particle_idx))
        p_system.update_to_object(context)
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
        elif solver_name == "VERLET":
            p_system.solver = solver.VerletSolver()
        elif solver_name == "LEAPFROG":
            p_system.solver = solver.LeapfrogSolver()
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

class AddWallCollisionOperator(bpy.types.Operator):
    bl_idname = "collision.wall"
    bl_label = "Add wall collision"
    bl_description = "add wall collision"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        current_collection = bpy.data.collections.get("Collision")
        if current_collection == None:
            current_collection = utils.create_collection(context.scene.collection, "Collision")
        plane_ob = utils.create_plane(current_collection, 'Wall collision', Vector((0.0, 0.0, -4.0)))
        wall_collision = collision.WallCollision(plane_ob)
        p_system.add_collision(wall_collision)
        return {'FINISHED'}

class AddParticleCollisionOperator(bpy.types.Operator):
    bl_idname = "collision.particle"
    bl_label = "Add particle collision"
    bl_description = "add particle collision"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        p_system.add_collision(collision.ParticleCollision())
        return {'FINISHED'}

class AddAngularConstraintOperator(bpy.types.Operator):
    bl_idname = "constraint.angular"
    bl_label = "Add angular constraint"
    bl_description = "add angular constraint"

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        axis_particle_idx = int(bpy.context.scene.axis_particle_idx)
        pair_particle_1_idx = int(bpy.context.scene.pair_particle_1_idx)
        pair_particle_2_idx = int(bpy.context.scene.pair_particle_2_idx)
        angular_constraint = constraint.AngularConstraint()
        angular_constraint.axis_particle_idx = axis_particle_idx
        angular_constraint.pair_particle_idx = pair_particle_1_idx, pair_particle_2_idx
        p_system.add_constraint(angular_constraint)
        return {'FINISHED'}


class SaveInitParticleSystemOperator(bpy.types.Operator):
    bl_idname = "particle_system.save_init"
    bl_label = "Save init particle system"
    bl_description = "save init particle system"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        particle_system.ParticleSystem.save_init_system(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event): # See comments at end  [1]
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class LoadInitParticleSystemOperator(bpy.types.Operator):
    bl_idname = "particle_system.load_init"
    bl_label = "Load init particle system"
    bl_description = "load init particle system"

    filepath = bpy.props.StringProperty(subtype="FILE_PATH")

    def execute(self, context):
        particle_system.ParticleSystem.load_init_system(self.filepath)
        return {'FINISHED'}

    def invoke(self, context, event): # See comments at end  [1]
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class SaveParticleSystemAnimationOperator(bpy.types.Operator):
    bl_idname = "particle_system.save_animation"
    bl_label = "Save particle system animation"
    bl_description = "save particle system animation"

    directory = bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        p_system.save_animation(self.directory)
        return {'FINISHED'}

    def invoke(self, context, event): # See comments at end  [1]
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class LoadParticleSystemAnimationOperator(bpy.types.Operator):
    bl_idname = "particle_system.load_animation"
    bl_label = "Load particle system animation"
    bl_description = "load particle system animation"

    directory = bpy.props.StringProperty(subtype="DIR_PATH")

    def execute(self, context):
        p_system = particle_system.ParticleSystem.get_instance()
        p_system.load_animation(self.directory)
        return {'FINISHED'}

    def invoke(self, context, event): # See comments at end  [1]
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class ParticleSimulationPanel(bpy.types.Panel):
    bl_idname = "PARTICLE_PT_SIMULATION"
    bl_label = "particle simulation panel"
    bl_category = "Particle System"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        layout = self.layout
        # scene = context.scene

        # FIXME solver update while loading init
        row = layout.row()
        row.prop(context.scene, "solver_name")
        row.operator('apply.solver', text="apply solver")

        row = layout.row()
        row.operator('delete_system.particle', text="delete particle system")
        row.operator('particle_system.save_init', text="save init particle system")
        row.operator('particle_system.load_init', text="load init particle system")
        row = layout.row()
        row.operator('particle_system.save_animation', text="save particle system animation")
        row.operator('particle_system.load_animation', text="load particle system animation")

        row = layout.row()
        row.prop(context.scene, "modify_particle_location", text="Realtime modify particle location")
        row = layout.row()
        row.operator('apply_constant_force.particle', text="apply constant force")
        row = layout.row()
        row.operator('apply_damping_force.particle', text="apply damping force")
        row = layout.row()
        row.prop(context.scene, 'spring_particle_idx', text="spring particle")
        row.operator('apply_spring_force.particle', text="apply spring force")
        row = layout.row()
        row.operator('particle.calculate_frame', text="calculate frame")
        row = layout.row()
        row.operator('particle_system.mass_spring_system', text="mass spring system")
        row.operator('particle_system.cloth_mass_spring_system', text="cloth system")
        row = layout.row()
        row.prop(context.scene, 'axis_particle_idx', text="axis particle")
        row.prop(context.scene, 'pair_particle_1_idx', text="pair particle 1")
        row.prop(context.scene, 'pair_particle_2_idx', text="pair particle 2")
        row.operator('constraint.angular', text="add angular constraint")
        row = layout.row()
        row.operator('collision.wall', text="add wall collision")
        row.operator('collision.particle', text="add particle collision")
        row = layout.row()
        row.operator('add.particle', text="add particle")


        row = layout.row()
        row.separator()
        row.prop(context.scene, 'select_particle_idx', text="particle list")
        if context.scene.select_particle_idx != "None":
            p_system = particle_system.ParticleSystem.get_instance()
            particle_idx = int(context.scene.select_particle_idx)
            if particle_idx < len(p_system.init_particle_list):
                p_system.draw(context, layout, particle_idx)
                row.operator('remove.particle', text="remove particle")

        row = layout.row()
        row.separator()
        row.prop(context.scene, 'force_name', text="force list")
        if context.scene.force_name != "None":
            p_system = particle_system.ParticleSystem.get_instance()
            force_idx = int(context.scene.force_name)
            if force_idx < len(p_system.force_list):
                p_system.force_list[force_idx].draw(context, layout)
                row.operator('force.remove', text="remove current force")

        row = layout.row()
        row.separator()
        row.prop(context.scene, 'constraint_name', text="constraint list")
        if context.scene.constraint_name != "None":
            p_system = particle_system.ParticleSystem.get_instance()
            constraint_idx = int(context.scene.constraint_name)
            p_system.constraint_list[constraint_idx].draw(context, layout)
#            row.operator('force.remove', text="remove current force")


def particle_item_callback(self, context):
    p_system = particle_system.ParticleSystem.get_instance()
    enum_prop_list = []
    for i, force in enumerate(p_system.init_particle_list):
        enum_prop_list.append((str(i), str(i), str(i)))
    if len(enum_prop_list) == 0:
        enum_prop_list.append(("None", "None", "None"))
    return enum_prop_list

def force_item_callback(self, context):
    p_system = particle_system.ParticleSystem.get_instance()
    enum_prop_list = []
    for i, force in enumerate(p_system.force_list):
        enum_prop_list.append((str(i), str(i) + " " + type(force).__name__, str(i) + " " + type(force).__name__))
    if len(enum_prop_list) == 0:
        enum_prop_list.append(("None", "None", "None"))
    return enum_prop_list

def constraint_item_callback(self, context):
    p_system = particle_system.ParticleSystem.get_instance()
    enum_prop_list = []
    for i, constraint in enumerate(p_system.constraint_list):
        enum_prop_list.append((str(i), str(i) + " " + type(constraint).__name__, str(i) + " " + type(constraint).__name__))
    if len(enum_prop_list) == 0:
        enum_prop_list.append(("None", "None", "None"))
    return enum_prop_list

def solver_item_callback(self, context):
    return (
        ('FOREULER', 'Forward Euler', "Forward euler solver"),
        ('2RK', '2nd order RK', "2nd order runge kutta solver"),
        ('4RK', '4th order RK', "4th order runge kutta solver"),
        ('VERLET', 'Verlet', "Verlet solver"),
        ('LEAPFROG', 'Leapfrog', "Leapfrog solver"),
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
    bpy.utils.register_class(AddWallCollisionOperator)
    bpy.utils.register_class(AddParticleCollisionOperator)
    bpy.utils.register_class(AddAngularConstraintOperator)
    bpy.utils.register_class(SaveInitParticleSystemOperator)
    bpy.utils.register_class(LoadInitParticleSystemOperator)
    bpy.utils.register_class(SaveParticleSystemAnimationOperator)
    bpy.utils.register_class(LoadParticleSystemAnimationOperator)

    bpy.utils.register_class(custom_prop.ParticleProp)
    bpy.utils.register_class(custom_prop.ConstantForceProp)
    bpy.utils.register_class(custom_prop.DampingForceProp)
    bpy.utils.register_class(custom_prop.SpringForceProp)
    bpy.utils.register_class(custom_prop.AngularConstraintProp)

    bpy.types.Scene.modify_particle_location = BoolProperty(name="modify_particle_location", update=modify_particle_update)
    bpy.types.Scene.spring_particle_idx = bpy.props.EnumProperty(name="spring_particle_idx", items=particle_item_callback)
    bpy.types.Scene.solver_name = bpy.props.EnumProperty(name="solver_name", items=solver_item_callback)
    bpy.types.Scene.particle_property = bpy.props.PointerProperty(type=custom_prop.ParticleProp)
    bpy.types.Scene.constant_force_vector = bpy.props.PointerProperty(type=custom_prop.ConstantForceProp)
    bpy.types.Scene.damping_constant = bpy.props.PointerProperty(type=custom_prop.DampingForceProp)
    bpy.types.Scene.spring_force = bpy.props.PointerProperty(type=custom_prop.SpringForceProp)
    bpy.types.Scene.angular_constraint = bpy.props.PointerProperty(type=custom_prop.AngularConstraintProp)
    bpy.types.Scene.axis_particle_idx = bpy.props.EnumProperty(name="axis_particle_idx", items=particle_item_callback)
    bpy.types.Scene.pair_particle_1_idx = bpy.props.EnumProperty(name="pair_particle_1_idx", items=particle_item_callback)
    bpy.types.Scene.pair_particle_2_idx = bpy.props.EnumProperty(name="pair_particle_2_idx", items=particle_item_callback)
    bpy.types.Scene.select_particle_idx = bpy.props.EnumProperty(name="select_particle_idx", items=particle_item_callback)
    bpy.types.Scene.force_name = bpy.props.EnumProperty(name="force_name", items=force_item_callback)
    bpy.types.Scene.constraint_name = bpy.props.EnumProperty(name="constraint_name", items=constraint_item_callback)

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
    bpy.utils.unregister_class(AddWallCollisionOperator)
    bpy.utils.unregister_class(AddParticleCollisionOperator)
    bpy.utils.unregister_class(AddAngularConstraintOperator)
    bpy.utils.unregister_class(SaveInitParticleSystemOperator)
    bpy.utils.unregister_class(LoadInitParticleSystemOperator)
    bpy.utils.unregister_class(SaveParticleSystemAnimationOperator)
    bpy.utils.unregister_class(LoadParticleSystemAnimationOperator)


    bpy.utils.unregister_class(custom_prop.ParticleProp)
    bpy.utils.unregister_class(custom_prop.ConstantForceProp)
    bpy.utils.unregister_class(custom_prop.DampingForceProp)
    bpy.utils.unregister_class(custom_prop.SpringForceProp)
    bpy.utils.unregister_class(custom_prop.AngularConstraintProp)

    del bpy.types.Scene.modify_particle_location
    del bpy.types.Scene.solver_name
    del bpy.types.Scene.particle_property
    del bpy.types.Scene.constant_force_vector
    del bpy.types.Scene.damping_constant
    del bpy.types.Scene.spring_force
    del bpy.types.Scene.angular_constraint
    del bpy.types.Scene.axis_particle_idx
    del bpy.types.Scene.pair_particle_1_idx
    del bpy.types.Scene.pair_particle_2_idx
    del bpy.types.Scene.angular_constraint
    del bpy.types.Scene.angular_constraint
    del bpy.types.Scene.select_particle_idx
    del bpy.types.Scene.force_name
    del bpy.types.Scene.constraint_name


if __name__ == "__main__":
    register()
