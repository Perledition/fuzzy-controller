# import standard modules

# import third party modules
from scipy.interpolate import interp1d

# import project related modules
from matplotlib import pyplot as plt


class Membership:
    """
    Class that performs membership specific tasks. Like calculating the degree of truth for a given value. Fit is the
    main function to initialize a new Membership with new members.

    :param: measure: str: (empty string default): defines in measure unit of measure the members are measured -
                          cosmetics for plotting.
    """

    def __init__(self, measure: str = ""):
        self.memberships = None    # placeholder for each dict with all members
        self.name = ""             # name of the object
        self.max_value = 0         # max value on x axis
        self.min_value = 0         # min value on y axis
        self.measure = measure     # description of base unit of measure

    def get_membership_degree(self, value: float):
        """
        for a given input value get the degrees of truth for each member available in the Membership object.

        :param value: float: value for which degrees of truth are of interest

        :return: returns memberships with an additional degree value
        """

        # prevent edge case that input value is higher or lower than defined scale
        if value > self.max_value:
            value = self.max_value

        elif value < self.min_value:
            value = self.min_value

        # calculate the degree of truth for a given value for each member available in Membership object
        # therefore the interpolation function is used
        for category, values in self.memberships.items():

            if (value >= values["lower_end"]) and (value <= values["upper_end"]):
                values["degree"] = float(values["coordinates"]["degree_func"](value))

            else:
                values["degree"] = 0

        return self.memberships

    def get_member(self, name: str):
        """
        get a member of the Membership object by it's name e.g "slow" if existing

        :param name: str: name of the member

        :return: dict of member, default or error case empty dict

        """
        try:
            return self.memberships[name]
        except KeyError:
            print("name is not valid for this group")
            return dict()

    def _contribute_max_min(self, value: float):
        """
        class internal function to find the x and y values of a Membership object over all members
        :param value: float: x coordinate value of a member

        :return: None
        """

        # if value is larger than current max value set value as new max. Same logic vise versa for min
        if value > self.max_value:
            self.max_value = value
        elif value < self.min_value:
            self.min_value = value

    def fit(self, members: dict, name: str = ""):
        """
        make the initialization of the Memberships objects members.

        :param members: dict: holding all members and ist lower, center and upper values
        :param name: str: name of the Membership object. Empty string default

        :return: None
        """

        # set input parameters to global attributes
        self.memberships = members
        self.name = name

        # iterate over each member and its values (lower, center, upper) in order to set the write values
        # get the max and min values and to set a interpolation function to create an easy access to all y values
        # at a given x value.
        for category, values in self.memberships.items():

            # find the min and max x values
            for x in list(values.values()):
                self._contribute_max_min(x)

            # defines the y values for each member. since only triangles supported it always as 3 binary values
            x_values = list(values.values())
            if len(set(x_values[:2])) == 1:
                y_values = [1, 1, 0]
            elif len(set(x_values[1:])) == 1:
                y_values = [0, 1, 1]
            else:
                y_values = [0, 1, 0]

            # add member specific coordinates with x's y's and function to get the degree of truth for a certain
            # x input. will be accessible in self.memberships[category]
            values["coordinates"] = {"x": x_values, "y": y_values, "degree_func": interp1d(x_values, y_values)}

    def show(self):
        """
        plots all class members.

        :return: None but displays graph
        """

        for category, values in self.memberships.items():
            plt.plot(values["coordinates"]["x"], values["coordinates"]["y"], label=category)

        plt.title(self.name)
        plt.xticks(self.measure)
        plt.legend()
        plt.show()



