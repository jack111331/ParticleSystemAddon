import bpy
from mathutils import Vector, Matrix
from .wall import Wall

class Collision:
    def project_collision(self, particle_system):
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

class ParticleCollision(Collision):
    def project_collision(self, particle_system):
        pass