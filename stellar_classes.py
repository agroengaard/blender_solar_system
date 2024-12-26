import bpy
import bmesh
import math

from mathutils import Vector

class SolarSystem:
    def __init__(self, size, frame_start=1, frame_end=250):
        self.size = size
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.bodies = []
        
    def add_body(self, body):
        self.bodies.append(body)

    def _calculate_all_body_interactions(self):
        bodies_copy = self.bodies.copy()
        for idx, first in enumerate(bodies_copy):
            for second in bodies_copy[idx + 1:]:
                first.accelerate_due_to_gravity(second)

    def _update_all(self):
        self.bodies.sort(key=lambda item: item.position[0])
        for body in self.bodies:
            body.move()
            body.set_location_keyframe(frame=self.current_frame)
            
            
    def create_animation(self):
        for self.current_frame in range(self.frame_start, self.frame_end):
            self._calculate_all_body_interactions()
            self._update_all()



class StellarBody:
    """
    Any object with mass in a solar system
    """
    min_display_size = 0.01
    display_log_base = 1.3
    
    def __init__(self, name, mass, position=(0, 0, 0), velocity=(0, 0, 0)):
        self.name = name
        self.mass = mass
        self.position = Vector(position)
        self.velocity = Vector(velocity)
        
        self.radius = max(
            math.log(self.mass, self.display_log_base),
            self.min_display_size,
        )
          
        self._add_sphere()
        self.obj.location = self.position
        
    def _add_sphere(self):
        """
        Based on dimalis answer here:
        https://blender.stackexchange.com/questions/93298/create-a-uv-sphere-object-in-blender-from-python
        """
        mesh = bpy.data.meshes.new(self.name)
        self.obj = bpy.data.objects.new(self.name, mesh)

        bpy.context.collection.objects.link(self.obj)

        bpy.context.view_layer.objects.active = self.obj
        self.obj.select_set(True)
     
        bm = bmesh.new()
        bmesh.ops.create_uvsphere(bm, u_segments=32, v_segments=16, radius=self.radius)
        bm.to_mesh(mesh)
        bm.free()

        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.ops.object.shade_smooth()
     
    def move(self):
        self.position = (
            self.position[0] + self.velocity[0],
            self.position[1] + self.velocity[1],
            self.position[2] + self.velocity[2],
        ) 
        self.obj.location = self.position
    
    def set_location_keyframe(self, frame):
        self.obj.keyframe_insert(data_path="location", frame=frame)
        
    def accelerate_due_to_gravity(self, other):
        distance = Vector(other.position) - Vector(self.position)
        distance_mag = distance.magnitude

        force_mag = self.mass * other.mass / (distance_mag ** 2)
        distance.normalize()
        force = distance * force_mag

        reverse = 1
        for body in self, other:
            acceleration = force / body.mass
            body.velocity += acceleration * reverse
            reverse = -1
            
