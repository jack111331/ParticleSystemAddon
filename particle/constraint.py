import bpy
from mathutils import Vector, Matrix, Quaternion
from .custom_prop import AngularConstraintProp
import math


class Constraint:
    def __init__(self):
        self.type = ''
    def apply_constraint(self, particle_system):
        pass

    def save_constraint(self, particle_system):
        pass

    def load_constraint(self, json_data, particle_system):
        pass

class PinConstraint(Constraint):
    def __init__(self):
        self.type = 'pre'
        self.pin_list = []

    def add_pin(self, particle, location):
        self.pin_list.append((particle, location))

    def apply_constraint(self, particle_system):
        for pin in self.pin_list:
            particle, location = pin

            particle.velocity = Vector((0.0, 0.0, 0.0))
            particle.force = Vector((0.0, 0.0, 0.0))
            particle.location = location

    def save_constraint(self, particle_system):
        json_data = {}
        json_data['constraint_name'] = 'pin_constraint'
        pin_list_data = []
        for pin in self.pin_list:
            pin_data = {}
            pin_data['pin_particle_idx'] = particle_system.get_particle_idx(pin[0])
            pin_data['pin_location'] = [pin[1].x, pin[1].y, pin[1].z]
            pin_list_data.append(pin_data)
        json_data['pin_list'] = pin_list_data
        return json_data

    def load_constraint(self, json_data, particle_system):
        self.pin_list = []
        for pin_data in json_data['pin_list']:
            pin_particle = particle_system.particle_list[pin_data['pin_particle_idx']]
            pin_location = Vector((pin_data['pin_location'][0], pin_data['pin_location'][1], pin_data['pin_location'][2]))
            self.pin_list.append((pin_particle, pin_location))

class AxisConstraint(Constraint):
    def __init__(self):
        self.type = 'pre'
        self.axis_list = []

    def add_pin(self, particle, axis='x'):
        axis_vector = Vector((1.0, 1.0, 1.0))
        if axis.lower() == 'x':
            axis_vector = Vector((1.0, 0.0, 0.0))
        if axis.lower() == 'y':
            axis_vector = Vector((0.0, 1.0, 0.0))
        if axis.lower() == 'z':
            axis_vector = Vector((0.0, 0.0, 1.0))
        self.axis_list.append((particle, axis_vector))

    def apply_constraint(self, particle_system):
        for pin in self.axis_list:
            particle, axis_vector = pin
            particle.velocity = particle.velocity * axis_vector
            particle.force = Vector((0.0, 0.0, 0.0))

    def save_constraint(self, particle_system):
        json_data = {}
        json_data['constraint_name'] = 'axis_constraint'
        axis_list_data = []
        for axis in self.axis_list:
            axis_data = {}
            axis_data['axis_particle_idx'] = particle_system.get_particle_idx(axis[0])
            axis_data['axis_vector'] = [axis[1].x, axis[1].y, axis[1].z]
            axis_list_data.append(axis_data)
        json_data['axis_list'] = axis_list_data
        return json_data

    def load_constraint(self, json_data, particle_system):
        self.axis_list = []
        for axix_data in json_data['axis_list']:
            axis_particle = particle_system.particle_list[axix_data['axis_particle_idx']]
            axis_vector = Vector((axix_data['axis_vector'][0], axix_data['axis_vector'][1], axix_data['axis_vector'][2]))
            self.axis_list.append((axis_particle, axis_vector))

class PlaneConstraint(Constraint):
    def __init__(self):
        self.type = 'pre'
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

    def save_constraint(self, particle_system):
        json_data = {}
        json_data['constraint_name'] = 'plane_constraint'
        plane_list_data = []
        for plane in self.plane_list:
            plane_data = {}
            plane_data['plane_particle_idx'] = particle_system.get_particle_idx(plane[0])
            plane_data['plane_vector'] = [plane[1].x, plane[1].y, plane[1].z]
            plane_list_data.append(plane_data)
        json_data['plane_list'] = plane_list_data
        return json_data

    def load_constraint(self, json_data, particle_system):
        self.plane_list = []
        for plane_data in json_data['plane_list']:
            plane_particle = particle_system.particle_list[plane_data['plane_particle_idx']]
            plane_vector = Vector((plane_data['plane_vector'][0], plane_data['plane_vector'][1], plane_data['plane_vector'][2]))
            self.plane_list.append((plane_particle, plane_vector))

class AngularConstraint(Constraint):
    # https://www.cs.rpi.edu/~cutler/classes/advancedgraphics/S07/final_projects/mulley_bittarelli.pdf
    # FIXME bug
    def __init__(self):
        self.type = 'post'
        self.axis_particle_idx = None
        self.pair_particle_idx = None, None
        self.min_angle = 0.3
        self.max_angle = 0.9
        # also constraint length version
        # In the condition where a, b length is fixed, we can obtain the minimum and maximum distance using cos property

    def draw(self, context, layout):
        row = layout.row()
        bpy.context.scene.angular_constraint.min_angle.foreach_set((self.min_angle,))
        row.prop(context.scene.angular_constraint, "min_angle", text="Min angle")
        bpy.context.scene.angular_constraint.max_angle.foreach_set((self.max_angle,))
        row.prop(context.scene.angular_constraint, "max_angle", text="Max angle")
        AngularConstraintProp.angular_constraint_reference = self

    def save_constraint(self, particle_system):
        json_data = {}
        json_data['constraint_name'] = 'angular_constraint'
        json_data['axis_particle_idx'] = self.axis_particle_idx
        json_data['pair_particle_idx_1'] = self.pair_particle_idx[0]
        json_data['pair_particle_idx_2'] = self.pair_particle_idx[1]
        json_data['min_angle'] = self.min_angle
        json_data['max_angle'] = self.max_angle
        return json_data

    def load_constraint(self, json_data, particle_system):
        self.axis_particle_idx = json_data['axis_particle_idx']
        self.pair_particle_idx = json_data['pair_particle_idx_1'], json_data['pair_particle_idx_2']
        self.min_angle = json_data['min_angle']
        self.max_angle = json_data['max_angle']

    def assign_axis_particle(self, axis_particle):
        self.axis_particle = axis_particle

    def assign_pair_particle(self, pair_particle_1, pair_particle_2):
        self.pair_particle = pair_particle_1, pair_particle_2

    def assign_min_angle(self, min_angle):
        self.min_angle = min_angle

    def assign_max_angle(self, max_angle):
        self.max_angle = max_angle

    def apply_constraint(self, particle_system):
        #0.24 0.34
        axis_particle = particle_system.particle_list[self.axis_particle_idx]
        pair_particle = particle_system.particle_list[self.pair_particle_idx[0]], particle_system.particle_list[
            self.pair_particle_idx[1]]
        vector_1 = pair_particle[0].location - axis_particle.location
        vector_2 = pair_particle[1].location - axis_particle.location
        angle_val = vector_1.angle(vector_2)
        if angle_val < 1e-9:
            return
        if angle_val < self.min_angle:
            # v1.rotation_difference(v2) is the diff that rotate from v1 to v2
            da = (self.min_angle - angle_val) / (2 * angle_val)
            rotate_diff = vector_2.rotation_difference(vector_1)
            vector_1_rotated = vector_1.copy()
            da_temp = da
            while da_temp >= 1:
                vector_1_rotated.rotate(Quaternion().slerp(rotate_diff, 1.0))
                da_temp -= 1.0
            vector_1_rotated.rotate(Quaternion().slerp(rotate_diff, da_temp))
            pair_particle[0].location = axis_particle.location + vector_1_rotated

            rotate_diff = vector_1.rotation_difference(vector_2)
            vector_2_rotated = vector_2.copy()
            da_temp = da
            while da_temp >= 1:
                vector_2_rotated.rotate(Quaternion().slerp(rotate_diff, 1.0))
                da_temp -= 1.0
            vector_2_rotated.rotate(Quaternion().slerp(rotate_diff, da_temp))
            pair_particle[1].location = axis_particle.location + vector_2_rotated
        elif angle_val > self.max_angle:
            da = (angle_val - self.max_angle) / (2 * angle_val)
            rotate_diff = vector_1.rotation_difference(vector_2)
            vector_1_rotated = vector_1.copy()
            da_temp = da
            while da_temp >= 1:
                vector_1_rotated.rotate(Quaternion().slerp(rotate_diff, 1.0))
                da_temp -= 1.0
            vector_1_rotated.rotate(Quaternion().slerp(rotate_diff, da_temp))
            pair_particle[0].location = axis_particle.location + vector_1_rotated

            rotate_diff = vector_2.rotation_difference(vector_1)
            vector_2_rotated = vector_2.copy()
            da_temp = da
            while da_temp >= 1:
                vector_2_rotated.rotate(Quaternion().slerp(rotate_diff, 1.0))
                da_temp -= 1.0
            vector_2_rotated.rotate(Quaternion().slerp(rotate_diff, da_temp))
            pair_particle[1].location = axis_particle.location + vector_2_rotated

        vector_1 = pair_particle[0].location - axis_particle.location
        vector_2 = pair_particle[1].location - axis_particle.location
        angle_val = vector_1.angle(vector_2)
