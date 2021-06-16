import bpy
from mathutils import Vector, Matrix
from .wall import Wall
from math import tan, sin, cos


class Collision:
    def project_collision(self, particle_system):
        pass

    def save_collision(self):
        pass

    def load_collision(self, json_data):
        pass

class WallCollision(Collision):
    def __init__(self, plane_obj):
        self.wall = Wall(plane_obj)

    def project_collision(self, particle_system):
        # collision
        wall_location = self.wall.get_location()
        wall_normal = self.wall.get_normal()
        for particle in particle_system.particle_list:
            projection = (wall_location - particle.location).dot(wall_normal)
            is_inside_wall = projection > 0
            if is_inside_wall == True:
                particle.location += (2 * projection) * wall_normal
                particle.velocity = particle.velocity.reflect(wall_normal)

    def save_collision(self):
        json_data = {}
        json_data["collision_name"] = "wall_collision"
        wall_location = self.wall.get_location()
        json_data["wall_location"] = [wall_location.x, wall_location.y, wall_location.z]
        wall_normal = self.wall.get_normal()
        json_data["wall_normal"] = [wall_normal.x, wall_normal.y, wall_normal.z]
        return json_data

    def load_collision(self, json_data):
        wall_location = Vector((json_data["wall_location"][0], json_data["wall_location"][1], json_data["wall_location"][2]))
        self.wall.set_location(wall_location)
        wall_normal = Vector((json_data["wall_normal"][0], json_data["wall_normal"][1], json_data["wall_normal"][2]))
        self.wall.set_normal(wall_normal)

class ParticleCollision(Collision):
    def project_collision(self, particle_system):
        for i in range(len(particle_system.particle_list)):
            for j in range(i+1, len(particle_system.particle_list)):
                particle_i = particle_system.particle_list[i]
                particle_j = particle_system.particle_list[j]
                # Reference from https://www.sjsu.edu/faculty/watkins/collision.htm
                if particle_i.is_collision(particle_j):
                    velocity_i = particle_i.velocity.copy()
                    velocity_j = particle_j.velocity.copy()
                    mass_i = particle_i.mass
                    mass_j = particle_j.mass
                    normal = (particle_i.location - particle_j.location).normalized()
                    a = 2 * normal.dot(velocity_i - velocity_j) / (1.0 / mass_i + 1.0 / mass_j)

                    particle_i.velocity -= ((a / mass_i) * normal)
                    particle_j.velocity += ((a / mass_j) * normal)

    def save_collision(self):
        json_data = {}
        json_data["collision_name"] = "particle_collision"
        return json_data

class ClothCollision(Collision):
    def __init__(self):
        self.particle_location = None
        self.triangle_connection = []
        self.first = True

    def reset_collision(self, particle_system):
        self.particle_location = None
        self.triangle_connection = []
        self.first = True

    def project_collision(self, particle_system):
        if self.first == True:
            origin_state = particle_system.get_state()
            self.particle_location = origin_state[:, 0:3].copy()
            self.first = False
        else:
            # TODO
            origin_state = particle_system.get_state()
            for triangle in self.triangle_connection:
                t_1_idx = triangle[0]
                t_2_idx = triangle[1]
                t_3_idx = triangle[2]
                for particle in particle_system.particle_list:
                    pass
            # particle_location should update at the end
            self.particle_location = origin_state[:, 0:3].copy()
