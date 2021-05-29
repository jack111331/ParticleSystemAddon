import bpy
from mathutils import Vector, Matrix

class Constraint:
    def apply_constraint(self, particle_system):
        pass

class PinConstraint(Constraint):
    def __init__(self):
        self.pin_list = []

    def add_pin(self, particle, location):
        self.pin_list.append((particle, location))

    def apply_constraint(self, particle_system):
        for pin in self.pin_list:
            particle, location = pin

            particle.velocity = Vector((0.0, 0.0, 0.0))
            particle.force = Vector((0.0, 0.0, 0.0))
            particle.location = location

class AxisConstraint(Constraint):
    def __init__(self):
        self.axis_list = []

    def add_pin(self, particle, axis='x'):
        axis_vector = Vector((1.0, 1.0, 1.0))
        if axis.lower()=='x':
            axis_vector = Vector((1.0, 0.0, 0.0))
        if axis.lower()=='y':
            axis_vector = Vector((0.0, 1.0, 0.0))
        if axis.lower()=='z':
            axis_vector = Vector((0.0, 0.0, 1.0))
        self.axis_list.append((particle, axis_vector))

    def apply_constraint(self, particle_system):
        for pin in self.axis_list:
            particle, axis_vector = pin
            particle.velocity = particle.velocity * axis_vector
            particle.force = Vector((0.0, 0.0, 0.0))

class PlaneConstraint(Constraint):
    def __init__(self):
        self.plane_list = []

    def add_pin(self, particle, plane_axis='xy'):
        plane_vector = Vector((1.0, 1.0, 1.0))
        if 'x' not in plane_axis.lower():
            plane_vector[0] = 0.0
        if 'y' not in plane_axis.lower():
            plane_vector[1] = 0.0
        if 'z' not in plane_axis.lower():
            plane_vector[2] = 0.0
        self.plane_list.append((particle, plane_vector))

    def apply_constraint(self, particle_system):
        for pin in self.plane_list:
            particle, plane_vector = pin
            particle.velocity = particle.velocity * plane_vector
            particle.force = Vector((0.0, 0.0, 0.0))

