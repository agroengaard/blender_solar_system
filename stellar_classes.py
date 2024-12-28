import bpy
import bmesh
import math
import random

from mathutils import Vector

class SolarSystem:
    def __init__(self, size, frame_start=1, frame_end=250):
        self.size = size
        self.frame_start = frame_start
        self.frame_end = frame_end
        self.bodies = []
        
    def add_body(self, body):
        self.bodies.append(body)


    def create_asteroidbelt(self, n, inner_radius, outer_radius, mass_min=0.02, mass_max=0.1, v_min=1, v_max=2):
        """
        ---------------------------------------------------------------- 
        | Generate n asteroids between two circles in the xy-plane.    |
        ----------------------------------------------------------------
        | INPUT:
        |    n (int): Number of points to generate.
        |    inner_radius (float): Radius of the inner circle.
        |    outer_radius (float): Radius of the outer circle.
        |_______________________________________________________________
        """
        for i in range(n):
            t = i/(n - 1) if n > 1 else 0                                            # Interpolate radius between inner and outer circle
            radius = inner_radius + t*(outer_radius - inner_radius)
            angle = 2*math.pi*t                                                    # Calculate angle for distribution

            # Compute (x, y, z) coordinates
            x = radius * math.cos(angle)
            y = radius * math.sin(angle)
            z = 0                            # All points lie in the xy-plane

            # Compute tangential vector (perpendicular to radius in 2D) for velocity purposes
            magnitude = random.uniform(v_min, v_max)
 
            v_x = -radius * math.sin(angle) * magnitude
            v_y =  radius * math.cos(angle) * magnitude
            v_z = 0  # Tangent is also in the xy-plane

            name = "asteroid_" + str(i)
            mass = random.uniform(mass_min, mass_max)
            self.add_body(StellarBody(name, mass, position=(x, y, z), velocity=(v_x, v_y, v_z)))


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
    ===============================================================
    || Class for creating any object with mass in a solar system ||
    ===============================================================
    """
    min_display_size = 0.05
    max_display_size = 1
    display_log_base = 1.3
    
    def __init__(self, name, mass, position=(0, 0, 0), velocity=(0, 0, 0), **kwargs):
        self.name     = name
        self.mass     = mass
        self.position = Vector(position)
        self.velocity = Vector(velocity)
        self.fixed    = kwargs.get("fixed", False)
        self.radius   = max(math.log(self.mass, self.display_log_base),
                            self.min_display_size)
        self.radius   = min(self.max_display_size, self.radius)
          
        self._add_sphere()
        self._create_material()
        self.obj.location = self.position
        
    def _add_sphere(self):
        """
        -------------------------------------------------------------------------------------------------------- 
        | Based on dimalis answer here:                                                                        |
        | https://blender.stackexchange.com/questions/93298/create-a-uv-sphere-object-in-blender-from-python   |
        --------------------------------------------------------------------------------------------------------
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
        if self.fixed:
            self.obj.location = self.position
        else:
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


    def _create_material(self):
        material_name = "material_" + self.name
        material = bpy.data.materials.new(name=material_name)
        material.use_nodes = True

        nodes = material.node_tree.nodes
        links = material.node_tree.links

        for node in nodes:
            nodes.remove(node)

        emission_node = nodes.new(type='ShaderNodeEmission')
        emission_node.location = (-200, 0)
        emission_node.inputs['Color'].default_value = (1.0, 1.0, 0.0, 1.0)  # Yellow color (RGBA)
        emission_node.inputs['Strength'].default_value = 10.0  # Light intensity

        output_node = nodes.new(type='ShaderNodeOutputMaterial')
        output_node.location = (0, 0)

        links.new(emission_node.outputs['Emission'], output_node.inputs['Surface'])

        if self.obj.data.materials:
            self.obj.data.materials[0] = material
        else:
            self.obj.data.materials.append(material)            

 