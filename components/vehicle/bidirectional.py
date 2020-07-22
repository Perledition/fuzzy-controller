# import standard modules

# import third party modules

# import project related modules


class Car:

    def __init__(self, driver_type="defensive"):

        # the current velocity of the car measured in m/s and total distance in m
        self.velocity = 0
        self.distance = 0

        # meter per second this is assumed to be constant
        self.speed_increase = 5

        # check if driver type is valid input
        assert driver_type in ["defensive", "aggressive"],\
            "driver type needs to match defensive or aggressive"

        # set the distance to keep to the object in front in meters
        self.distance = {"defensive": 15, "aggressive": 5}[driver_type]

    def _measure_distance(self):
        pass

    def _time_to_crash(self):
        pass

    def _accelerate(self):
        pass

    def _deceleration(self):
        pass

    def _calculate_velocity(self):
        pass

    def update(self, second):
        pass

    def set_velocity(self, velocity):
        self.velocity = velocity

    def get_distance(self):
        return self.distance

    def get_velocity(self):
        return self.velocity


