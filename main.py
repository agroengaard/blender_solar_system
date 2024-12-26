
from stellar_classes import StellarBody, SolarSystem


if __name__ == "__main__":

    sun    = StellarBody("Sun", 10_000)
    planet = StellarBody("Planet_1", 10, position=(200, -50, 0), velocity=(0, 5, 0))


    solar_system = SolarSystem(1)
    solar_system.add_body(sun)
    solar_system.add_body(planet)
    solar_system.create_animation()
