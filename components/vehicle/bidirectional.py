# import standard modules

# import third party modules
from scipy.interpolate import interp1d

# import project related modules


class SimpleCar:

    def __init__(self, controller=None, adoption_rate=1):
        self.route = None
        self.adoption_rate = adoption_rate
        self.route_request = dict()
        self.distance_controller = controller
        self.velocity = 0
        self.distance = 0
        self.acceleration = 0
        self.history = {
            "velocity": [0],
            "acceleration": [0],
            "distance": [0]
        }

    @staticmethod
    def _calculate_acceleration(velocity, prev_velocity, seconds):

        try:
            acceleration = (velocity - prev_velocity)/seconds
            return acceleration

        except ZeroDivisionError:
            acceleration = 0
            return acceleration

    def _calculate_distance(self, velocity, acceleration, seconds, overwrite=False):

        # print("input params: ", velocity, acceleration, seconds)
        distance = abs((velocity*seconds) + 1/2*acceleration*(seconds**2))

        if overwrite:
            self.distance += distance
            return self.distance
        else:
            return distance

    # functions to calculate the leading car
    def _pre_calculate_route(self):

        # add a time indicator value to each tuple for better query capabilites
        second = 0
        route = [(0, 0, 0)]  # set route with initial values of 0 velocity, seconds to hold and absolut seconds

        for v, s in self.route:

            # add absolut second indicator in order to improve query capeabilites
            second += s
            route += [(v, s, second)]

        # overwrite route with copy and addtional absolut second count
        self.route = route

        # collect second, velocity, acceleration and distance for each milestone within the route
        sec = [s[2] for s in self.route]
        vel = [v[0] for v in self.route]
        # acc = [self._calculate_acceleration(x[0], x[1]) for x in self.route]

        dis_calculation = lambda vel, acc, sec: abs((vel*sec) + 1/2*acc*(sec**2))

        # calculate acceleration and distance for the milestones in order to make the values
        # available for a interpolation function
        distance = 0
        prev_velo = 0
        dis = list()
        acc = list()
        for pair in self.route:

            velo = pair[0]
            seconds = pair[1]

            const_acc = self._calculate_acceleration(velo, prev_velo, seconds)
            d = dis_calculation(velo, const_acc, seconds)
            prev_velo = velo
            distance += d
            acc.append(const_acc)
            dis.append(distance)

        # set interpolation functions for each attribute in order to request a specific second later on
        self.route_request["velocity"] = interp1d(sec, vel)
        self.route_request["acceleration"] = interp1d(sec, acc)
        self.route_request["distance"] = interp1d(sec, dis)

    def get_second(self, second):
        vel = self.route_request["velocity"](second)
        acc = self.route_request["acceleration"](second)
        dis = self.route_request["distance"](second)

        # print(f"second: {second} velocity: {vel} acceleration: {acc} distance: {dis}")
        return vel, acc, dis

    def set_route(self, route=None):
        assert type(route) == list,\
            "route must be list of tuples [(meter per second, time in seconds to keep velocity)]"

        self.route = route
        self._pre_calculate_route()

    def update(self, distance_to_leading_car, second):
        # set first an array for the fuzzy controller
        # define the current input for the fuzzy controller

        current = {
            "target_distance": distance_to_leading_car,
            "accel_crnt": self.acceleration,
            "vel_crnt": self.velocity
        }

        adjustment = self.distance_controller.run(current)

        self.acceleration += self.adoption_rate * adjustment

        # create a cap for acceleration in order to make the physics more realistic
        if self.acceleration > 2:
            self.acceleration = 2
        elif self.acceleration < -2:
            self.acceleration = -2

        self.distance += self._calculate_distance(self.velocity, self.acceleration, 1)

        if self.velocity < 0:
            self.velocity = 0
            self.acceleration = 0
        else:
            self.velocity += self.acceleration

        print(f"adjustment: {adjustment} velocity: {self.velocity} acceleration: {self.acceleration} distance: {self.distance}, lead_distance: {distance_to_leading_car}")
        self.history["velocity"].append(self.velocity)
        self.history["acceleration"].append(self.acceleration)
        self.history["distance"].append(self.distance)



