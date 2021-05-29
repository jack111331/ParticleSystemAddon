import bpy
from mathutils import geometry, Vector, Matrix
class Wall:
    def __init__(self, reference_ob):
        # Assume its plane
        self.reference_ob = reference_ob

    def get_location(self):
        return self.reference_ob.location

    def get_normal(self):
        return self.reference_ob.rotation_euler.to_matrix() @ Vector((0.0, 0.0, 1.0))

    def is_collision(self, point_location, point_vector):
        location = self.get_location()
        normal = self.get_normal()
        if point_vector.dot(normal) < 1e-9:
            return False, Vector((0, 0, 0))
        projection_location = geometry.intersect_line_plane(location, location+normal, point_location, point_vector)
        return True, projection_location