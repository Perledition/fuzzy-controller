
class SimpleCar:

    def __init__(self, route=None, distance_prev=0, controller=None, distance_lead=0):
        self.distance = -distance_lead  # measured in meter
        self.velocity = 0  # measured in meter/s
        self.acceleration = 0  # measured in meter/s*s
        self.route = route  # external provided route with list of milestones [(second, velocity), ...]
        self.route_step = 0  # current index of the route map
        self.last_acceleration = 0  # last known acceleration
        self.last_switch_acceleration = 0  # timestamp to which the acceleration was changed
        self.distance_prev = distance_prev  # distance to leading car used by driver
        self.distance_lead = distance_lead  # defines the distance to the leading car
        self.controller = controller  # FuzzyDistanceController defined
        self.blackbox = {  # captures the journey
            "distance": list(),
            "velocity": list(),
            "acceleration": list(),
            "target_distance": list()
        }

    def _route_step(self, t):

        # get the timestamp of the current route milestone
        try:
            timestamp_current = self.route[self.route_step][0]

            # if the current second is larger than the last route step
            # go one step ahead
            if t >= timestamp_current:
                self.route_step += 1
                return True

            else:
                return False

        # in case of an index error the route is over and the vehicle will remain constant
        except IndexError:
            return False

    def _blackbox_update(self):
        self.blackbox["distance"].append(self.distance)
        self.blackbox["velocity"].append(self.velocity)
        self.blackbox["acceleration"].append(self.acceleration)

        if self.route is None:
            self.blackbox["target_distance"].append(self.distance_lead)

    def _radar(self, distance_lead):
        self.distance_lead = distance_lead - self.distance
        assert self.distance_lead > 0, "crash!!!!"

    def _velocity(self, t):
        self.velocity += self.acceleration * t
        if self.velocity < 0:
            self.velocity = 0
        elif self.velocity > 20:
            self.velocity = 20

    def _acceleration(self, ms_crnt, ms_prev):

        if self.route is not None:
            delta_time = ms_crnt[0] - ms_prev[0]
            delta_vel = ms_crnt[1] - ms_prev[1]
            # print(f"delta t: {delta_time}, delta v {delta_vel}")
            self.acceleration = delta_vel/delta_time

            if self.acceleration > 20:
                self.acceleration = 20

        else:
            self.acceleration = 0

    def _distance(self, t):
        # calculation is absolute because its just a one directional movement (velocity -> speed)
        # since velocity would have also a direction. But our direction will always be positive
        self.distance += abs(0.5 * self.acceleration * (t**2))
        # self.distance += self.velocity * t

    def update(self, second, distance=500):

        # no route is available use fuzzy logic to adjust acceleration
        if self.route is None:

            # update the journey protocol
            self._blackbox_update()

            # second, distance, prev_distance
            self._radar(distance)


            # define the current input for the fuzzy controller
            current = {"target_distance": self.distance_lead,
                       "driver_type": self.distance_prev,
                       "change_of_distance": self.acceleration}
            # assign the controller output to the new acceleration
            self.last_acceleration = self.acceleration
            self.acceleration = self.controller.run(current)

            #if round(self.last_acceleration, 3) != round(self.acceleration, 3):
            # define how long the acceleration was constant
            timing = second - self.last_switch_acceleration
            self.last_switch_acceleration = second

            # update acceleration
            self._distance(timing)

            # update velocity
            self._velocity(timing)


            #else:
             #   self._blackbox_update()

        # if route is available check whether a new milestone is was reached
        elif self._route_step(second):
            try:
                # get new and previous milestone for further calculation
                ms_crnt = self.route[self.route_step]
                ms_prev = self.route[self.route_step - 1]

                # update acceleration
                self._acceleration(ms_crnt, ms_prev)

                # update velocity
                timing = ms_crnt[0] - ms_prev[0]
                self._velocity(timing)

                # update distance made
                self._distance(timing)  # timing

                # update the journey protocol
                self._blackbox_update()

            except IndexError:
                # in case of an index error the route is over and the vehicle will remain constant
                self._blackbox_update()

        else:
            self._blackbox_update()
