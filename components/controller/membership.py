# import standard modules
import warnings

# import third party modules
from scipy.interpolate import interp1d

# import project related modules
from matplotlib import pyplot as plt


class Membership:

    def __init__(self, measure=""):
        self.memberships = None
        self.name = ""
        self.max_value = 0
        self.min_value = 0
        self.measure = measure

    def get_membership_degree(self, value):

        if value > self.max_value:
            value = self.max_value
        elif value < self.min_value:
            value = self.min_value

        for category, values in self.memberships.items():

            if (value >= values["lower_end"]) and (value <= values["upper_end"]):
                values["degree"] = float(values["coordinates"]["degree_func"](value))

            else:
                values["degree"] = 0

        return self.memberships

    def get_member(self, name):
        try:
            return self.memberships[name]
        except KeyError:
            print("name is not valid for this group")
            return dict()

    def _contribute_max_min(self, value):
        if value > self.max_value:
            self.max_value = value
        elif value < self.min_value:
            self.min_value = value

    def fit(self, members, name=""):
        self.memberships = members
        self.name = name

        for category, values in self.memberships.items():

            for x in list(values.values()):
                self._contribute_max_min(x)

            x_values = list(values.values())
            if len(set(x_values[:2])) == 1:
                y_values = [1, 1, 0]
            elif len(set(x_values[1:])) == 1:
                y_values = [0, 1, 1]
            else:
                y_values = [0, 1, 0]

            values["coordinates"] = {"x": x_values, "y": y_values, "degree_func": interp1d(x_values, y_values)}

    def show(self):
        for category, values in self.memberships.items():
            plt.plot(values["coordinates"]["x"], values["coordinates"]["y"], label=category)

        plt.title(self.name)
        plt.xticks(self.measure)
        plt.legend()
        plt.show()



