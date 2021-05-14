import bpy
from .utils import getParticleSystem
from mathutils import Vector, Matrix

# Hand made a particle system and attach it to existing particle system in blender

# Base class
class Force:
    def draw(self, context, layout):
        pass

    def apply_force(self, particle):
        pass

class ConstantForce(Force):
    def __init__(self, force_constant=Vector((2.0, 2.0, 2.0))):
        self.forceforce_constant = force_constant

    def draw(self, context, layout):
        row.prop(self, "force_constant", text="Force constant")

    def apply_force(self, particle):
        particle.apply_force(self.force_constant)

class DampingForce(Force):
    def __init__(self, damp_constant=0.5):
        self.damp_constant = damp_constant

    def draw(self, context, layout):
        pass

    def apply_force(self, particle):
        # F = -cv
        location, velocity = particle.get_state()
        damped_force = -self.damp_constant * velocity
        particle.apply_force(damped_force)

class SpringForce(Force):
    def __init__(self, spring_constant, rest_location):
        self.spring_constant = spring_constant
        self.rest_location = rest_location

    def draw(self, context, layout):
        pass

    def apply_force(self, particle):
        #F = k(x – x0)
        location, velocity = particle.get_state()
        spring_force = self.spring_constant * (self.rest_location - location)
        particle.apply_force(spring_force)

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

class CoherentForce:
    def __init__(self):
        self.coherent_particle_list = []

    def apply_force(self, particle_system):
        pass

class SpringTwoParticleForce(CoherentForce):
    def __init__(self):
        super().__init__()
        self.spring_constant = 0.5
        self.rest_location_list = []

    def add_coherent(self, coherent_particle_tuple, rest_location):
        self.coherent_particle_list.append(coherent_particle_tuple)
        self.rest_location_list.append(rest_location)

    def apply_force(self, particle_system):
        #F = k(R – v_l) v/v_l
        for i in range(len(self.rest_location_list)):
            particle_1, particle_2 = self.coherent_particle_list[i][0], self.coherent_particle_list[i][1]
            location_1, _ = particle_1.get_state()
            location_2, _ = particle_2.get_state()
            location_vec = location_1 - location_2
            spring_force = self.spring_constant * (self.rest_location_list[i] - location_vec.length) * location_vec/location_vec.length
            particle_1.apply_force(spring_force)
            particle_2.apply_force(-spring_force)

# TODO viscous fluid

def add_constant_force(particle_system):
    pass
    # p_sys, p_sys_mod = getParticleSystem(ob)
    # print(p_sys, p_sys_mod)
    # frame_start = int(p_sys.settings.frame_start)
    # frame_end = int(p_sys.settings.frame_end)
    # print(frame_start, frame_end)
    # for i in range(frame_start, frame_end):
    #     bpy.context.scene.frame_set(i)
    #     for particle in p_sys.particles:
    #         particle.velocity = (1.0, 1.0, 1.0)
    #         # print(particle.location)

def add_damping_force(ob):
    p_sys, p_sys_mod = getParticleSystem(ob)
    print(p_sys, p_sys_mod)

def add_spring_force(ob):
    p_sys, p_sys_mod = getParticleSystem(ob)
    print(p_sys, p_sys_mod)
