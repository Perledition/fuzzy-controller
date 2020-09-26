# import standard modules

# import third party modules
from scipy.interpolate import interp1d

# import project related modules
from components.controller.fuzzy import FuzzyController


class SimpleCar:
    """
    The class is a basic definition of a car as object. it will either take a set of milestones and calculate the
    velocity, acceleration and driven distance over a given amount of time or use a fuzzy controller in order to
    calculate these values dynamically. The object does ignore dimensions like height, width, weight or oder similar
    attributes a car has in a real world. The class was written in order to mimic the most simple physics

    :param controller: FuzzyController: a predefined controller which does contain (target_distance, accel_crnt,
                                        vel_crnt, and acceleration. (default: None).
    :param adoption_rate: float: rate of adopting the fuzzy controllers recommendation (default 1.0)
    """

    def __init__(self, controller: FuzzyController = None, adoption_rate: float = 1.0):
        self.route = None                                  # list of tuples which define milestones of velocity and time
        self.adoption_rate = adoption_rate                 # sensitivity of fuzzy controller adoption
        self.route_request = dict()                        # placeholder - will hold value for a pre calculated route
        self.distance_controller = controller              # FuzzyController from the input parameters
        self.velocity = 0                                  # current velocity of the car
        self.distance = 0                                  # current distance driven by the car
        self.acceleration = 0                              # current acceleration of the car
        self.history = {                                   # values for vel, acc, distance at a given second (index)
            "velocity": [0],
            "acceleration": [0],
            "distance": [0]
        }

    @staticmethod
    def _calculate_acceleration(velocity: float, prev_velocity: float, seconds: int):
        """
        function does calculate a constant acceleration between to points of velocity and a given duration.

        :param velocity: float: velocity desired to archive within the duration (meter per second)
        :param prev_velocity: float: current or starting velocity (meter per second)
        :param seconds: int: seconds in which the desired velocity must be archived
        :return: float: returns a constant acceleration meter per second²
        """

        try:
            acceleration = (velocity - prev_velocity)/seconds
            return acceleration

        except ZeroDivisionError:
            acceleration = 0
            return acceleration

    def _calculate_distance(self, velocity: float, acceleration: float, seconds: int, overwrite=False):
        """
        calculates a distance archived by a given initial velocity, acceleration and a duration how long
        to keep the acceleration.

        :param velocity: float: current or initial velocity in meter per second
        :param acceleration: float: constant acceleration in meter per second²
        :param seconds: int: duration of how long to accelerate in seconds
        :param overwrite: boolean: parameter which defines, whether the overall distance should be overwritten
        :return: float: returns an archived distance in meter
        """

        # calculate distance over a time with a constant acceleration
        distance = abs((velocity*seconds) + 1/2*acceleration*(seconds**2))

        if overwrite:
            self.distance += distance
            return self.distance
        else:
            return distance

    #############################################
    #       functions for a leading car        #
    ############################################
    def _pre_calculate_route(self):
        """
        The function does pre calculate the entire values for acceleration, velocity and distance with a given route.
        After this function run successful the values for acceleration, velocity and distance at a given second can
        be requested.

        :return: None.
        """

        # add a time indicator value to each tuple for better query capabilities
        # remember - the route is a list of tuples with (velocity [m/s], duration in seconds)
        second = 0

        # set route with initial values of 0 velocity, seconds to hold and absolute seconds
        route = [(0, 0, 0)]

        for v, s in self.route:

            # add absolute second indicator in order to improve query capabilities
            second += s
            route += [(v, s, second)]

        # overwrite route with copy and additional absolute second count
        self.route = route

        # collect second, velocity, acceleration and distance for each milestone within the route
        sec = [s[2] for s in self.route]
        vel = [v[0] for v in self.route]

        # set a quick helper function to calculate distance
        dis_calculation = lambda vel, acc, sec: abs((vel*sec) + 1/2*acc*(sec**2))

        # calculate acceleration and distance for the milestones in order to make the values
        # available for a interpolation function
        distance = 0
        prev_velo = 0
        dis = list()
        acc = list()

        # pre calculate the values (distance, acceleration) for each milestone
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

    def get_second(self, second: int):
        """
        function takes a second and returns the interpolation value for velocity, acceleration and distance
        from a given route handed over previously. Make sure the second is within the handed over route timeline.

        :param second: int: defines a second.
        :return: tuple: velocity, acceleration and distance at second
        """

        # request interpolation function for each value and hand over the x value (second) in order to get the y value
        vel = self.route_request["velocity"](second)
        acc = self.route_request["acceleration"](second)
        dis = self.route_request["distance"](second)

        return vel, acc, dis

    def set_route(self, route: list = None):
        """
        All values (acceleration, velocity and distance) can be requested for a given second after setting the route.
        It is important to notice, that once a route is set a FuzzyController should not be initialized as well.

        :param route: list: of tuples [(meter per seconds, amount of seconds to hold desired velocity), ..]
        :return: None
        """
        assert type(route) == list,\
            "route must be list of tuples [(meter per second, time in seconds to keep velocity)]"

        self.route = route

        # pre calculate and interpolate the entire route
        self._pre_calculate_route()

    #############################################
    #       functions for a following car      #
    ############################################

    def update(self, distance_to_leading_car: float):
        """
        the function does update the values and history of the car with the initialized FuzzyController.
        If not FuzzyController was initialized originally the function will fail. Once updated the values
        can be found in the history. In order to access the history attribute type Car.history. With Car being your
        initialized class variable. Update should always be used for each second of an experiment.

        :param distance_to_leading_car: float: distance to the leading car or object
        :return: None
        """

        # set first an array for the fuzzy controller
        # define the current input for the fuzzy controller
        current = {
            "target_distance": distance_to_leading_car,
            "accel_crnt": self.acceleration,
            "vel_crnt": self.velocity
        }

        # run the fuzzy controller with the parameters and get the recommendation of the controller
        adjustment = self.distance_controller.run(current)

        # apply the recommended adjustment of the controller with a defined adoption rate (1.0 default)
        self.acceleration += self.adoption_rate * adjustment

        # create a cap for acceleration in order to make the physics more realistic
        if self.acceleration > 2:
            self.acceleration = 2
        elif self.acceleration < -2:
            self.acceleration = -2

        # update the distance of the car
        # the second is 1 because the update runs each second
        self.distance += self._calculate_distance(self.velocity, self.acceleration, 1)

        # since the car can only travel forward the velocity cannot be negative. Therefore make the velocity zero
        if self.velocity < 0:
            self.velocity = 0
            self.acceleration = 0
        else:
            self.velocity += self.acceleration

        # print a status update in the console and add the current values also to the history
        print(f"adjustment: {adjustment} velocity: {self.velocity} acceleration: {self.acceleration} distance: {self.distance}, lead_distance: {distance_to_leading_car}")
        self.history["velocity"].append(self.velocity)
        self.history["acceleration"].append(self.acceleration)
        self.history["distance"].append(self.distance)



