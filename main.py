import sys

sys.path.insert(3, "C:\\Repositories\\blender_solar_system")
 
from stellar_classes import StellarBody, SolarSystem

if __name__ == "__main__":
 
    sun     = StellarBody("Sun",   50,   position=(0, 0, 0), velocity=(0, 0, 0), fixed=True)
    earth   = StellarBody("Earth", 1,    position=(5, 0, 0), velocity=(0, 3, 0))
 
    solar_system = SolarSystem(1)
    solar_system.add_body(sun)
    solar_system.add_body(earth)
    solar_system.create_animation()
