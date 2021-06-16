import bpy
from .custom_prop import ConstantForceProp, DampingForceProp, SpringForceProp
from mathutils import Vector, Matrix

# Hand made a particle system and attach it to existing particle system in blender

# Base class
class Force:
    def draw(self, context, layout):
        pass

    def apply_force(self, particle):
        pass

    def save_force(self):
        pass

    def load_force(self, json_data):
        pass

class ConstantForce(Force):
    def __init__(self, force_constant=(2.0, 2.0, 2.0)):
        self.force_constant = force_constant

    def draw(self, context, layout):
        row = layout.row()
        bpy.context.scene.constant_force_vector.constant_force_vector.foreach_set(self.force_constant)
        row.prop(context.scene.constant_force_vector, "constant_force_vector", text="Force constant")
        ConstantForceProp.constant_force_reference = self

    def apply_force(self, particle):
        particle.apply_force(Vector(self.force_constant))

    def save_force(self):
        json_data = {}
        json_data["force_name"] = 'constant_force'
        json_data["constant_force"] = [self.force_constant[0], self.force_constant[1], self.force_constant[2]]
        return json_data

    def load_force(self, json_data):
        self.force_constant = (json_data['constant_force'][0], json_data['constant_force'][1], json_data['constant_force'][2])

class DampingForce(Force):
    def __init__(self, damp_constant=(0.5,)):
        self.damp_constant = damp_constant

    def draw(self, context, layout):
        row = layout.row()
        bpy.context.scene.damping_constant.damping_constant.foreach_set(self.damp_constant)
        row.prop(context.scene.damping_constant, "damping_constant", text="Damp constant")
        DampingForceProp.damping_force_reference = self

    def apply_force(self, particle):
        # F = -cv
        location, velocity = particle.get_state()
        damped_force = -self.damp_constant[0] * velocity
        particle.apply_force(damped_force)

    def save_force(self):
        json_data = {}
        json_data["force_name"] = 'damping_force'
        json_data["constant_damp"] = self.damp_constant[0]
        return json_data

    def load_force(self, json_data):
        self.damp_constant = (json_data['constant_damp'],)

class SpringForce(Force):
    def __init__(self, spring_constant = (0.5, ), rest_location = (0.5, 0.5, 0.5)):
        self.spring_constant = spring_constant
        self.rest_location = rest_location

    def draw(self, context, layout):
        row = layout.row()
        bpy.context.scene.spring_force.spring_constant.foreach_set(self.spring_constant)
        bpy.context.scene.spring_force.spring_rest_location.foreach_set(self.rest_location)
        row.prop(context.scene.spring_force, "spring_constant", text="Spring constant")
        row.prop(context.scene.spring_force, "spring_rest_location", text="Spring vector")
        SpringForceProp.spring_force_reference = self

    def apply_force(self, particle):
        #F = k(x – x0)
        location, velocity = particle.get_state()
        spring_force = self.spring_constant[0] * (Vector(self.rest_location) - location)
        particle.apply_force(spring_force)

    def save_force(self):
        json_data = {}
        json_data["force_name"] = 'spring_force'
        json_data["constant_spring"] = self.spring_constant[0]
        json_data["rest_location"] = [self.rest_location[0], self.rest_location[1], self.rest_location[2]]
        return json_data

    def load_force(self, json_data):
        self.spring_constant = (json_data['constant_spring'],)
        self.rest_location = (json_data['rest_location'][0], json_data['rest_location'][1], json_data['rest_location'][2])

class GravityForce(Force):
    def __init__(self):
        self.gravity_constant = 9.8

    def draw(self, context, layout):
        pass

    def apply_force(self, particle):
        #F = k(x – x0)
        mass = particle.mass
        gravity_force = Vector((0.0, 0.0, -mass * self.gravity_constant))
        particle.apply_force(gravity_force)

    def save_force(self):
        json_data = {}
        json_data["force_name"] = 'gravity_force'
        return json_data


class CoherentForce:
    def __init__(self):
        self.coherent_particle_list = []

    def apply_force(self, particle_system):
        pass

    def save_force(self, particle_system):
        pass

    def load_force(self, json_data, particle_system):
        pass

class SpringTwoParticleForce(CoherentForce):
    def __init__(self):
        super().__init__()
        self.spring_constant = 4.0
        self.rest_length_list = []

    def add_coherent(self, coherent_particle_tuple, rest_length):
        self.coherent_particle_list.append(coherent_particle_tuple)
        self.rest_length_list.append(rest_length)

    def apply_force(self, particle_system):
        #F = k(R – v_l) v/v_l
        for i in range(len(self.rest_length_list)):
            particle_1, particle_2 = self.coherent_particle_list[i][0], self.coherent_particle_list[i][1]
            location_1, _ = particle_1.get_state()
            location_2, _ = particle_2.get_state()
            location_vec = location_1 - location_2
            spring_force = self.spring_constant * (self.rest_length_list[i] - location_vec.length) * location_vec/location_vec.length
            particle_1.apply_force(spring_force)
            particle_2.apply_force(-spring_force)

    def save_force(self, particle_system):
        json_data = {}
        json_data['coherent_force_name'] = 'spring_two_particle_force'
        coherent_particle_list_data = []
        for i, coherent_particle in enumerate(self.coherent_particle_list):
            coherent_particle_data = {}
            coherent_particle_data['coherent_particle_idx'] = [particle_system.get_particle_idx(coherent_particle[0]), particle_system.get_particle_idx(coherent_particle[1])]
            coherent_particle_data['rest_length'] = self.rest_length_list[i]
            coherent_particle_list_data.append(coherent_particle_data)
        json_data['coherent_particle_list'] = coherent_particle_list_data
        json_data['spring_constant'] = self.spring_constant
        return json_data

    def load_force(self, json_data, particle_system):
        self.rest_length_list = []
        self.coherent_particle_list = []
        self.spring_constant = json_data['spring_constant']
        for coherent_particle_data in json_data['coherent_particle_list']:
            coherent_particle = (particle_system.particle_list[coherent_particle_data['coherent_particle_idx'][0]],
                                 particle_system.particle_list[coherent_particle_data['coherent_particle_idx'][1]])
            rest_length = coherent_particle_data['rest_length']
            self.add_coherent(coherent_particle, rest_length)

# TODO viscous fluid
