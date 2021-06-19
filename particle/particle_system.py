import bpy
from mathutils import Vector, Matrix
from .utils import getParticleSystem, create_collection, create_sphere, create_connect_line, create_plane
from .apply_force import ConstantForce, SpringTwoParticleForce, GravityForce, DampingForce, SpringForce
from .solver import ForwardEulerSolver, SecondOrderRKSolver, FourthOrderRKSolver, VerletSolver, LeapfrogSolver, BackwardEulerSolver
from .constraint import PinConstraint, AxisConstraint, PlaneConstraint, AngularConstraint
from .collision import ParticleCollision, WallCollision
from .custom_prop import ParticleProp
import numpy as np
import math
import json

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

    def save_particle(self):
        json_data = {}
        json_data["location"] = [self.location.x, self.location.y, self.location.z]
        json_data["velocity"] = [self.velocity.x, self.velocity.y, self.velocity.z]
        json_data["mass"] = self.mass
        return json_data

    def load_particle(self, json_data):
        self.location = Vector((json_data["location"][0], json_data["location"][1], json_data["location"][2]))
        self.velocity = Vector((json_data["velocity"][0], json_data["velocity"][1], json_data["velocity"][2]))
        self.mass = json_data["mass"]

    def set_state(self, particle_state):
        self.location[0] = particle_state[0]
        self.location[1] = particle_state[1]
        self.location[2] = particle_state[2]
        self.velocity[0] = particle_state[3]
        self.velocity[1] = particle_state[4]
        self.velocity[2] = particle_state[5]

    def is_collision(self, another_particle):
        return (self.location - another_particle.location).length_squared <= (self.mass + another_particle.mass)**2

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

    @classmethod
    def save_init_system(cls, filepath='init_part.json'):
        if cls.instance != None:
            self = cls.instance
            json_data = {}
            json_data["particle_list"] = []
            for init_particle in self.init_particle_list:
                json_data["particle_list"].append(init_particle.save_particle())

            json_data["force_list"] = []
            for force in self.force_list:
                json_data["force_list"].append(force.save_force())

            json_data["coherent_force_list"] = []
            for coherent_force in self.coherent_force_list:
                json_data["coherent_force_list"].append(coherent_force.save_force(self))

            json_data["constraint_list"] = []
            for constraint in self.constraint_list:
                json_data["constraint_list"].append(constraint.save_constraint(self))

            json_data["collision_list"] = []
            for collision in self.collision_detect_list:
                json_data["collision_list"].append(collision.save_collision())

            json_data["solver"] = self.solver.save_solver()

            if not filepath.endswith('.json'):
                filepath += '.json'

            with open(filepath, 'w') as fp:
                json.dump(json_data, fp)

    @classmethod
    def load_init_system(cls, filepath='init_part.json'):
        if cls.instance == None:
            cls.instance = ParticleSystem()

        self = cls.instance
        with open(filepath, 'r') as fp:
            json_data = json.load(fp)

            self.init_particle_list = []
            self.particle_list = []
            for init_particle_data in json_data["particle_list"]:
                self.add_particle().load_particle(init_particle_data)

            self.force_list = []
            for force_data in json_data["force_list"]:
                if force_data['force_name'] == 'constant_force':
                    self.add_force(ConstantForce()).load_force(force_data)
                elif force_data['force_name'] == 'damping_force':
                    self.add_force(DampingForce()).load_force(force_data)
                elif force_data['force_name'] == 'spring_force':
                    self.add_force(SpringForce()).load_force(force_data)
                elif force_data['force_name'] == 'gravity_force':
                    self.add_force(GravityForce()).load_force(force_data)

            self.coherent_force_list = []
            for coherent_force_data in json_data["coherent_force_list"]:
                # TODO
                if coherent_force_data['coherent_force_name'] == 'spring_two_particle_force':
                    self.add_coherent_force(SpringTwoParticleForce()).load_force(coherent_force_data, self)

            self.constraint_list = []
            for constraint_data in json_data["constraint_list"]:
                if constraint_data['constraint_name'] == 'pin_constraint':
                    self.add_constraint(PinConstraint()).load_constraint(constraint_data, self)
                elif constraint_data['collision_name'] == 'axis_constraint':
                    self.add_constraint(AxisConstraint()).load_constraint(constraint_data, self)
                elif constraint_data['collision_name'] == 'plane_constraint':
                    self.add_constraint(PlaneConstraint()).load_constraint(constraint_data, self)
                elif constraint_data['collision_name'] == 'angular_constraint':
                    self.add_constraint(AngularConstraint()).load_constraint(constraint_data, self)

            self.collision_detect_list = []
            for collision_data in json_data["collision_list"]:
                if collision_data['collision_name'] == 'wall_collision':
                    current_collection = bpy.data.collections.get("Collision")
                    if current_collection == None:
                        current_collection = create_collection(bpy.context.scene.collection, "Collision")
                    plane_ob = create_plane(current_collection, 'Wall collision', Vector((0.0, 0.0, -4.0)))
                    self.add_collision(WallCollision(plane_ob)).load_collision(collision_data)
                elif collision_data['collision_name'] == 'particle_collision':
                    self.add_collision(ParticleCollision()).load_collision(collision_data)

            if json_data['solver'] == 'forward_euler_solver':
                self.solver = ForwardEulerSolver()
            elif json_data['solver'] == 'second_order_rk_solver':
                self.solver = SecondOrderRKSolver()
            elif json_data['solver'] == 'fourth_order_rk_solver':
                self.solver = FourthOrderRKSolver()
            elif json_data['solver'] == 'verlet_solver':
                self.solver = VerletSolver()
            elif json_data['solver'] == 'leap_frog_solver':
                self.solver = LeapfrogSolver()
            elif json_data['solver'] == 'backward_euler_solver':
                self.solver = BackwardEulerSolver()



    def draw(self, context, layout, particle_idx):
        row = layout.row()
        bpy.context.scene.particle_property.init_location.foreach_set(self.init_particle_list[particle_idx].location)
        bpy.context.scene.particle_property.init_velocity.foreach_set(self.init_particle_list[particle_idx].velocity)
        bpy.context.scene.particle_property.init_mass.foreach_set((self.init_particle_list[particle_idx].mass, ))

        row.label(text="Initialize property")
        row.operator('particle.sync_init', text="Sync initial state")
        row = layout.row()
        row.prop(context.scene.particle_property, "init_location", text="Location")
        row.prop(context.scene.particle_property, "init_velocity", text="Velocity")
        row.prop(context.scene.particle_property, "init_mass", text="Mass")
        ParticleProp.particle_reference = self.init_particle_list[particle_idx]

    def get_particle_idx(self, particle):
        return self.particle_list.index(particle)

    def add_particle(self, location=Vector((0.0, 0.0, 0.0)), velocity=Vector((0.0, 0.0, 0.0)), force=Vector((0.0, 0.0, 0.0)), mass=1.0):
        particle = Particle(location, velocity, force, mass)
        init_particle = Particle(location, velocity, force, mass)
        self.particle_list.append(particle)
        self.init_particle_list.append(init_particle)
        return init_particle

    def remove_particle(self, i):
        self.particle_list.pop(i)
        self.init_particle_list.pop(i)

    def add_force(self, force):
        self.force_list.append(force)
        return force

    def add_coherent_force(self, coherent_force):
        self.coherent_force_list.append(coherent_force)
        return coherent_force

    def add_constraint(self, constraint):
        self.constraint_list.append(constraint)
        return constraint

    def add_collision(self, collision):
        self.collision_detect_list.append(collision)
        return collision

    def get_dim(self):
        return 6 * len(self.particle_list)

    def get_state(self):
        particle_state = np.zeros((len(self.particle_list), 6))
        for i in range(len(self.particle_list)):
            location, velocity = self.particle_list[i].get_state()
            particle_state[i, 0] = location[0]
            particle_state[i, 1] = location[1]
            particle_state[i, 2] = location[2]
            particle_state[i, 3] = velocity[0]
            particle_state[i, 4] = velocity[1]
            particle_state[i, 5] = velocity[2]
        return particle_state

    def set_state(self, particle_state):
        for i in range(len(self.particle_list)):
            self.particle_list[i].set_state(particle_state[i, 0:6])

    def derivative_eval(self):
        for particle in self.particle_list:
            particle.clear_force()

        for force in self.force_list:
            for particle in self.particle_list:
                force.apply_force(particle)

        for coherent_force in self.coherent_force_list:
            coherent_force.apply_force(self)

        for constraint in self.constraint_list:
            if constraint.type == 'pre':
                constraint.apply_constraint(self)

        particle_deriv_state = np.zeros((len(self.particle_list), 6))
        for i in range(len(self.particle_list)):
            velocity, acceleration = self.particle_list[i].derivative_eval()
            particle_deriv_state[i, 0] = velocity[0]
            particle_deriv_state[i, 1] = velocity[1]
            particle_deriv_state[i, 2] = velocity[2]
            particle_deriv_state[i, 3] = acceleration[0]
            particle_deriv_state[i, 4] = acceleration[1]
            particle_deriv_state[i, 5] = acceleration[2]

        return particle_deriv_state

    def save_animation(self, animation_dir):
        particle_count = len(self.particle_list)
        while particle_count < len(self.init_particle_list):
            self.particle_list.pop()
            particle_count = particle_count-1
        while particle_count > len(self.init_particle_list):
            self.particle_list.append(Particle())
            particle_count = particle_count+1

        for j in range(len(self.init_particle_list)):
            self.particle_list[j].location = self.init_particle_list[j].location.copy()
            self.particle_list[j].velocity = self.init_particle_list[j].velocity.copy()
            self.particle_list[j].mass = self.init_particle_list[j].mass

        json_data = {}
        json_data["particle_list"] = []
        json_data["frame_start"] = bpy.context.scene.frame_start
        json_data["frame_end"] = bpy.context.scene.frame_end
        for particle in self.particle_list:
            particle_data = {}
            particle_data["location"] = [particle.location.x, particle.location.y, particle.location.z]
            particle_data["velocity"] = [particle.velocity.x, particle.velocity.y, particle.velocity.z]
            particle_data["mass"] = particle.mass
            json_data["particle_list"].append(particle_data)

        init_animation_filepath = animation_dir + "config.json"
        with open(init_animation_filepath, 'w') as fp:
            json.dump(json_data, fp)

        self.solver.reset_solver(self)
        self.save_particle_animation(animation_dir, 0)
        for i in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end):
            self.solver.solve_step(self, 0.05)
            # Constraint reapply
            for constraint in self.constraint_list:
                if constraint.type == 'post':
                    constraint.apply_constraint(self)
            for collision in self.collision_detect_list:
                collision.project_collision(self)
            self.save_particle_animation(animation_dir, i)

    def save_particle_animation(self, output_dir, frame):
        json_data = {}
        json_data["particle_list"] = []
        for particle in self.particle_list:
            particle_data = {}
            particle_data["location"] = [particle.location.x, particle.location.y, particle.location.z]
            json_data["particle_list"].append(particle_data)

        animation_filepath = output_dir + str(frame) + ".json"
        with open(animation_filepath, 'w') as fp:
            json.dump(json_data, fp)

    def load_animation(self, input_dir):
        init_animation_filepath = input_dir + 'config.json'
        current_collection = bpy.data.collections.get("Custom Particle System")
        if current_collection == None:
            current_collection = create_collection(bpy.context.scene.collection, "Custom Particle System")

        bpy.context.scene.frame_set(0)
        with open(init_animation_filepath, 'r') as fp:
            json_data = json.load(fp)

            frame_start = json_data["frame_start"]
            frame_end = json_data["frame_end"]
            self.init_particle_list = []
            self.particle_list = []
            for init_particle_data in json_data["particle_list"]:
                self.add_particle().load_particle(init_particle_data)

            object_count = len(current_collection.objects)
            while object_count < len(self.init_particle_list):
                create_sphere(current_collection, str(object_count), self.init_particle_list[object_count].location)
                object_count = object_count + 1
            while object_count > len(self.init_particle_list):
                current_collection.objects.unlink(current_collection.objects.get(str(object_count - 1)))
                object_count = object_count - 1

        for j in range(len(self.init_particle_list)):
            particle_ob = current_collection.objects.get(str(j))
            particle_ob.scale = Vector(
                (self.init_particle_list[j].mass, self.init_particle_list[j].mass, self.init_particle_list[j].mass))

        for i in range(frame_start, frame_end):
            animation_filepath = input_dir + str(i) + '.json'
            with open(animation_filepath, 'r') as fp:
                json_data = json.load(fp)
                for j in range(len(self.particle_list)):
                    particle_ob = current_collection.objects.get(str(j))
                    particle_ob.location = Vector((json_data['particle_list'][j]['location'][0], json_data['particle_list'][j]['location'][1], json_data['particle_list'][j]['location'][2]))
                    particle_ob.keyframe_insert(data_path="location", frame=i)

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

        particle_count = len(self.particle_list)
        while particle_count < len(self.init_particle_list):
            self.particle_list.pop()
            particle_count = particle_count-1
        while particle_count > len(self.init_particle_list):
            self.particle_list.append(Particle())
            particle_count = particle_count+1

        if calculate_frame == False:
            for i in range(len(self.init_particle_list)):
                particle_ob = current_collection.objects.get(str(i))
                particle_ob.location = self.init_particle_list[i].location
        else:
            bpy.context.scene.frame_set(0)
            for j in range(len(self.init_particle_list)):
                self.particle_list[j].location = self.init_particle_list[j].location.copy()
                self.particle_list[j].velocity = self.init_particle_list[j].velocity.copy()
                self.particle_list[j].mass = self.init_particle_list[j].mass
                particle_ob = current_collection.objects.get(str(j))
                particle_ob.scale = Vector((self.init_particle_list[j].mass, self.init_particle_list[j].mass, self.init_particle_list[j].mass))

            self.solver.reset_solver(self)
            for i in range(bpy.context.scene.frame_start, bpy.context.scene.frame_end):
                self.solver.solve_step(self, 0.05)
                # Constraint reapply
                print("frame ", i)
                for constraint in self.constraint_list:
                    if constraint.type == 'post':
                        constraint.apply_constraint(self)
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
        while len(p_system.init_particle_list) < particle_amount:
            p_system.add_particle()
        while len(p_system.init_particle_list) > particle_amount:
            p_system.remove_particle(len(p_system.init_particle_list) - 1)

        pin_constraint = PinConstraint()
        for i in range(self.row):
            for j in range(self.col):
                particle_idx = i*self.col + j
                location = Vector((HORIZONTAL_LENGTH * j, 0.0, -VERTICAL_LENGTH * i))
                p_system.init_particle_list[particle_idx].location = location
                if i == 0 and (j == 0 or j == self.col-1):
                    pin_constraint.add_pin(p_system.particle_list[particle_idx], location)
        p_system.add_constraint(pin_constraint)
        p_system.update_to_object(bpy.context, False)

        current_collection = bpy.data.collections.get("Custom Particle System")
        line_collection = bpy.data.collections.get("Line Connection")
        if line_collection == None:
            line_collection = create_collection(bpy.context.scene.collection, "Line Connection")
        # Structural force

        structural_force = SpringTwoParticleForce()
        # FIXME rest_length determine
        structural_rest_length = self.rest_length
        for i in range(self.row):
            for j in range(self.col):
                if i-1 >= 0:
                    create_connect_line(line_collection, current_collection.objects.get(str((i-1)*self.col+j)), current_collection.objects.get(str(i*self.col+j)))
                    structural_force.add_coherent((p_system.particle_list[(i-1)*self.col+j], p_system.particle_list[i*self.col+j]), structural_rest_length)
                if i+1 < self.row:
                    create_connect_line(line_collection, current_collection.objects.get(str(i*self.col+j)), current_collection.objects.get(str((i+1)*self.col+j)))
                    structural_force.add_coherent((p_system.particle_list[i*self.col+j], p_system.particle_list[(i+1)*self.col+j]), structural_rest_length)
                if j-1 >= 0:
                    create_connect_line(line_collection, current_collection.objects.get(str(i*self.col+j-1)), current_collection.objects.get(str(i*self.col+j)))
                    structural_force.add_coherent((p_system.particle_list[i*self.col+j-1], p_system.particle_list[i*self.col+j]), structural_rest_length)
                if j+1 < self.col:
                    create_connect_line(line_collection, current_collection.objects.get(str(i*self.col+j)), current_collection.objects.get(str(i*self.col+j+1)))
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