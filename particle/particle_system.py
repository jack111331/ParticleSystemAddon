import bpy
from mathutils import Vector, Matrix
from .utils import getParticleSystem, create_collection, create_sphere
from .apply_force import SpringTwoParticleForce, GravityForce, DampingForce
from .solver import ForwardEulerSolver
from .constraint import PinConstraint
from .custom_prop import ParticleProp
import numpy as np
import math

class Particle:
    def __init__(self, location=Vector((0.0, 0.0, 0.0)), velocity=Vector((0.0, 0.0, 0.0)), force=Vector((0.0, 0.0, 0.0)), mass=1.0):
        # location and velocity is visible to outer
        self.location = location
        self.velocity = velocity
        self.force = force
        self.mass = mass

    def clear_force(self):
        self.force = Vector((0.0, 0.0, 0.0))

    def apply_force(self, force):
        self.force += force

    def derivative_eval(self):
        return self.velocity, self.force / self.mass

    def get_state(self):
        return self.location, self.velocity

    def set_state(self, particle_state):
        self.location[0] = particle_state[0]
        self.location[1] = particle_state[1]
        self.location[2] = particle_state[2]
        self.velocity[0] = particle_state[3]
        self.velocity[1] = particle_state[4]
        self.velocity[2] = particle_state[5]


class ParticleSystem:
    instance = None
    def __init__(self):
        self.init_particle_list = []
        self.particle_list = []
        self.force_list = []
        self.coherent_force_list = []
        self.constraint_list = []
        self.collision_detect_list = []
        self.time_step = 0.0
        self.collection = None
        self.solver = ForwardEulerSolver()
        self.frame_start = 1
        self.frame_end = 250

    @classmethod
    def get_instance(cls):
        if cls.instance == None:
            cls.instance = ParticleSystem()
        return cls.instance

    @classmethod
    def delete_instance(cls):
        if cls.instance != None:
            del cls.instance
            cls.instance = None

    def draw(self, context, layout, particle_idx):
        row = layout.row()
        getitem_func = bpy.context.scene.particle_property.init_location.__getitem__
        print("Before", self.init_particle_list[particle_idx].location, (getitem_func(0), getitem_func(1), getitem_func(2)))
        bpy.context.scene.particle_property.init_location.foreach_set(self.init_particle_list[particle_idx].location)
        getitem_func = bpy.context.scene.particle_property.init_location.__getitem__
        print("After", self.init_particle_list[particle_idx].location, (getitem_func(0), getitem_func(1), getitem_func(2)))
        bpy.context.scene.particle_property.init_velocity.foreach_set(self.init_particle_list[particle_idx].velocity)
        bpy.context.scene.particle_property.init_mass.foreach_set((self.init_particle_list[particle_idx].mass, ))
        row.prop(context.scene.particle_property, "init_location", text="Initial location")
        row.prop(context.scene.particle_property, "init_velocity", text="Initial velocity")
        row.prop(context.scene.particle_property, "init_mass", text="Initial mass")
        ParticleProp.particle_reference = self.init_particle_list[particle_idx]

    def add_particle(self, location=Vector((0.0, 0.0, 0.0)), velocity=Vector((0.0, 0.0, 0.0)), force=Vector((0.0, 0.0, 0.0)), mass=1.0):
        particle = Particle(location, velocity, force, mass)
        init_particle = Particle(location, velocity, force, mass)
        self.particle_list.append(particle)
        self.init_particle_list.append(init_particle)

    def remove_particle(self, i):
        self.particle_list.pop(i)
        self.init_particle_list.pop(i)

    def add_force(self, force):
        self.force_list.append(force)

    def add_coherent_force(self, coherent_force):
        self.coherent_force_list.append(coherent_force)

    def add_constraint(self, constraint):
        self.constraint_list.append(constraint)

    def add_collision(self, collision):
        self.collision_detect_list.append(collision)

    def get_dim(self):
        return 6 * len(self.particle_list)

    def get_state(self):
        particle_state = np.zeros((6*len(self.particle_list)))
        for i in range(len(self.particle_list)):
            location, velocity = self.particle_list[i].get_state()
            particle_state[6*i] = location[0]
            particle_state[6*i+1] = location[1]
            particle_state[6*i+2] = location[2]
            particle_state[6*i+3] = velocity[0]
            particle_state[6*i+4] = velocity[1]
            particle_state[6*i+5] = velocity[2]
        return particle_state

    def set_state(self, particle_state):
        for i in range(len(self.particle_list)):
            self.particle_list[i].set_state(particle_state[6*i:6*(i+1)])

    def derivative_eval(self):
        for particle in self.particle_list:
            particle.clear_force()

        for force in self.force_list:
            for particle in self.particle_list:
                force.apply_force(particle)

        for coherent_force in self.coherent_force_list:
            coherent_force.apply_force(self)

        for constraint in self.constraint_list:
            constraint.apply_constraint(self)

        particle_deriv_state = np.zeros((6 * len(self.particle_list)))
        for i in range(len(self.particle_list)):
            velocity, acceleration = self.particle_list[i].derivative_eval()
            particle_deriv_state[6*i] = velocity[0]
            particle_deriv_state[6*i+1] = velocity[1]
            particle_deriv_state[6*i+2] = velocity[2]
            particle_deriv_state[6*i+3] = acceleration[0]
            particle_deriv_state[6*i+4] = acceleration[1]
            particle_deriv_state[6*i+5] = acceleration[2]

        return particle_deriv_state

    def update_to_object(self, context, calculate_frame=False):
        current_collection = bpy.data.collections.get("Custom Particle System")
        if current_collection == None:
            current_collection = create_collection(context.scene.collection, "Custom Particle System")
        object_count = len(current_collection.objects)
        while object_count < len(self.init_particle_list):
            create_sphere(current_collection, str(object_count), self.init_particle_list[object_count].location)
            object_count = object_count + 1
        while object_count > len(self.init_particle_list):
            current_collection.objects.unlink(current_collection.objects.get(str(object_count-1)))
            object_count = object_count-1

        if calculate_frame == False:
            for i in range(len(self.init_particle_list)):
                particle_ob = current_collection.objects.get(str(i))
                particle_ob.location = self.init_particle_list[i].location
        else:
            bpy.context.scene.frame_set(0)
            for j in range(len(self.init_particle_list)):
                self.particle_list[j].location = self.init_particle_list[j].location.copy()
                self.particle_list[j].velocity = self.init_particle_list[j].velocity.copy()

            for i in range(self.frame_start, self.frame_end):
                self.solver.solve_step(self, 0.05)
                for collision in self.collision_detect_list:
                    collision.project_collision(self)
                for j in range(len(self.particle_list)):
                    particle_ob = current_collection.objects.get(str(j))
                    particle_ob.location = self.particle_list[j].location
                    particle_ob.keyframe_insert(data_path="location", frame=i)

class MassSpringSystem:
    def __init__(self, advance=False):
        self.row = 7
        self.col = 7
        self.stiffness_constant = 0.2
        self.rest_length = 4.0

        p_system = ParticleSystem.get_instance()
        particle_amount = self.row * self.col
        HORIZONTAL_LENGTH = 3.0
        VERTICAL_LENGTH = 3.0
        while len(p_system.particle_list) < particle_amount:
            p_system.add_particle()
        while len(p_system.particle_list) > particle_amount:
            p_system.remove_particle(len(p_system.particle_list) - 1)

        pin_constraint = PinConstraint()
        for i in range(self.row):
            for j in range(self.col):
                particle_idx = i*self.col + j
                location = Vector((HORIZONTAL_LENGTH * j, 0.0, -VERTICAL_LENGTH * i))
                p_system.particle_list[particle_idx].location = location
                if i == 0 and (j == 0 or j == self.col-1):
                    pin_constraint.add_pin(p_system.particle_list[particle_idx], location)
        p_system.add_constraint(pin_constraint)

        # Structural force
        structural_force = SpringTwoParticleForce()
        # FIXME rest_length determine
        structural_rest_length = self.rest_length
        for i in range(self.row):
            for j in range(self.col):
                if i-1 >= 0:
                    structural_force.add_coherent((p_system.particle_list[(i-1)*self.col+j], p_system.particle_list[i*self.col+j]), structural_rest_length)
                if i+1 < self.row:
                    structural_force.add_coherent((p_system.particle_list[i*self.col+j], p_system.particle_list[(i+1)*self.col+j]), structural_rest_length)
                if j-1 >= 0:
                    structural_force.add_coherent((p_system.particle_list[i*self.col+j-1], p_system.particle_list[i*self.col+j]), structural_rest_length)
                if j+1 < self.col:
                    structural_force.add_coherent((p_system.particle_list[i*self.col+j], p_system.particle_list[i*self.col+j+1]), structural_rest_length)
        p_system.add_coherent_force(structural_force)

        if advance == True:
            # Shear force
            shear_force = SpringTwoParticleForce()
            shear_rest_length = self.rest_length * math.sqrt(2)
            for i in range(self.row):
                for j in range(self.col):
                    if i - 1 >= 0 and j-1 >= 0:
                        shear_force.add_coherent(
                            (p_system.particle_list[(i - 1) * self.col + j-1], p_system.particle_list[i * self.col + j]),
                            shear_rest_length)
                    if i + 1 < self.row and j-1 >= 0:
                        shear_force.add_coherent(
                            (p_system.particle_list[i * self.col + j], p_system.particle_list[(i + 1) * self.col + j-1]),
                            shear_rest_length)
                    if i-1 >= 0 and j + 1 < self.col:
                        shear_force.add_coherent(
                            (p_system.particle_list[(i-1) * self.col + j + 1], p_system.particle_list[i * self.col + j]),
                            shear_rest_length)
                    if i+1 < self.row and j + 1 < self.col:
                        shear_force.add_coherent(
                            (p_system.particle_list[i * self.col + j], p_system.particle_list[(i+1) * self.col + j + 1]),
                            shear_rest_length)

            # Flexion force
            flexion_force = SpringTwoParticleForce()
            flexion_rest_length = 2 * self.rest_length
            for i in range(self.row):
                for j in range(self.col):
                    if i - 2 >= 0:
                        flexion_force.add_coherent(
                            (p_system.particle_list[(i - 2) * self.col + j], p_system.particle_list[i * self.col + j]),
                            flexion_rest_length)
                    if i + 2 < self.row:
                        flexion_force.add_coherent(
                            (p_system.particle_list[i * self.col + j], p_system.particle_list[(i + 2) * self.col + j]),
                            flexion_rest_length)
                    if j - 2 >= 0:
                        flexion_force.add_coherent(
                            (p_system.particle_list[i * self.col + j - 2], p_system.particle_list[i * self.col + j]),
                            flexion_rest_length)
                    if j + 2 < self.col:
                        flexion_force.add_coherent(
                            (p_system.particle_list[i * self.col + j], p_system.particle_list[i * self.col + j + 2]),
                            flexion_rest_length)

            p_system.add_coherent_force(shear_force)
            p_system.add_coherent_force(flexion_force)

        gravity_force = GravityForce()
        p_system.add_force(gravity_force)

        damping_force = DampingForce()
        p_system.add_force(damping_force)