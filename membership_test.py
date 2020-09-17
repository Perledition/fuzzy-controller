import pandas as pd
import warnings
from matplotlib import pyplot as plt
from scipy.interpolate import interp1d
from components.controller.activation import PolygonGravity
from experiment.intervals import accel, settings
from shapely.geometry import Polygon
from shapely.geometry import LineString, Point

accel_crnt = {
    "strong negative": {"lower_end": -2, "center": -2, "upper_end": -1},
    "negative": {"lower_end": -2, "center": -1, "upper_end": 0},
    "zero": {"lower_end": -2, "center": 0, "upper_end": 2},
    "positive": {"lower_end": 0, "center": 1, "upper_end": 2},
    "strong positive": {"lower_end": 1, "center": 2, "upper_end": 2}
}


class Membership:

    def __init__(self):
        self.memberships = None
        self.name = ""
        self.max_value = 0
        self.min_value = 0

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
            print(values)
            plt.plot(values["coordinates"]["x"], values["coordinates"]["y"], label=category)

        plt.title(self.name)
        plt.legend()
        plt.show()


class FuzzyDistanceController(object):

    def __init__(self):

        # feature space / inputs to measure memberships
        self.feature_space = None

        # rule set applied for inference
        self.rules = None

        # output space defined by user - needs to follow the same structure as input
        self.output = None

    def _fuzzification(self, conditions: dict):

        # initialize empty dict as fallback return value
        perception = dict()

        try:
            # calculate the memberships for each category and make them available in dict structure for further process.
            for category, value in conditions.items():
                memberships = self.feature_space[category].get_membership_degree(value)
                perception[category] = memberships

            # return dict in structure {"category_name": {"member": membership_confidence, ....}}
            return perception

        except (TypeError, KeyError) as exc:
            warnings.warn("fuzzification was not successfull, make sure your inputs match your settings")
            return dict()

    @staticmethod
    def _query_generator(category_members):

        # generate a query value combinations from category and related values - is needed to keep the query dynamic
        for cat, members in category_members.items():

            # query string must include a or condition - since a category can have multiple members true
            # to a certain degree
            query_string = " | ".join(f"({cat}=='{mem}')" for mem in members)
            yield query_string

    def _get_rule_subset(self, perception: dict):

        # initialize resulting dict
        category_members = dict()
        for category, members in perception.items():

            # set a list for the current category so members can be collected
            category_members[category] = list()

            for key, value in members.items():

                if abs(value["degree"]) > 0:
                    category_members[category].append(key)

        # create a subset of the given rules - copy complete data set and filter afterwards to ensure
        # other memory location and prevent overwriting
        subset = self.rules.loc[:, :]

        q = list()
        # create query conditions and filter the given data set for conditions
        for query in self._query_generator(category_members):
            if query != "":
                q.append(query)

        return subset.query("&".join(f"({qy})" for qy in q))

    def _inference(self, perception: dict):

        # filter subset of rules that match the perception - filter because the rest is not needed and can be ignored
        subset = self._get_rule_subset(perception)

        # get interval relevant columns - with the name of memberships
        valid_columns = list(perception.keys())
        for column in valid_columns:

            memberships = perception[column]
            subset[f"{column}_value"] = subset.apply(lambda row: memberships[row[column]]["degree"], axis=1)

        subset["degree"] = subset.loc[:, [f"{column}_value" for column in valid_columns]].sum(axis='columns') / len(valid_columns)

        # create a set of fuzzy outputs [{"output category": "member", "degree": value of degree}, ...]
        result = subset.loc[:, ["acceleration", "degree"]].to_dict("r")
        print("result: ", result)
        return result

    @staticmethod
    def _get_intersection(a, b, c, d):
        line1 = LineString([a, b])
        line2 = LineString([c, d])

        int_pt = line1.intersection(line2)
        point_of_intersection = int_pt.x, int_pt.y
        return point_of_intersection

    def _member_centroid_generator(self, fuzzy_results):

        results = list()
        for f_set in fuzzy_results:

            # set variables - member name and degree to which the member is true
            member = f_set[self.output.name]
            degree = f_set["degree"]

            coordinates = self.output.get_member(member)["coordinates"]

            # create polygon coordinates in order to calculate centroid for group
            x = coordinates["x"]
            y = coordinates["y"]

            x1 = (x[0], y[0])
            x2 = self._get_intersection(x1, (x[1], y[1]), (x[0], degree), (x[2], degree))
            x3 = self._get_intersection((x[1], y[1]), (x[2], y[2]), (x[0], degree), (x[2], degree))
            x4 = (x[2], y[2])

            # calculate the centroid for the polygon generated by a certain confidence degree
            poly = Polygon([x1, x2, x3, x4])

            results.append({"member": member, "degree": degree, "centroid": tuple(poly.centroid.coords)[0]})

        return results

    def _defuzzification(self, fuzzy_results):

        # get the centroid of each member area, to make the output area usable as absolute value
        centroid_data = self._member_centroid_generator(fuzzy_results)

        # create an action value from the center of gravities
        action = 0
        for result in centroid_data:
            try:
                # deg_action = (weight * result["output"])
                if result["degree"] != 0:
                    action += result["degree"] * result["centroid"][0]

            except ZeroDivisionError:
                continue

        # print(f"len: {len(actions)}, set: {len(list(set(actions)))}, action: {sum(actions)}")
        # action = sum(list(set(actions)))/len(list(set(actions)))
        return action

    def set_ruleset(self, rules: pd.DataFrame):

        # set self.rules (required rule set) if object type is a pandas data frame: data frame is used to make
        # the code more readable and understandable
        if type(rules) is pd.DataFrame:
            self.rules = rules
            return True
        else:
            return False

    def set_inputs(self, feature_space: dict):

        # ensure empty feature_space - edge case
        self.feature_space = dict()
        try:

            # create a MembershipValidator object for each category - the validator calculates the memberships
            # the objects will be stored in self.feature_space
            for category, setup in feature_space.items():
                assert type(setup) is dict, f"{category} does not contain a setup dict, create a dict"
                mem = Membership()
                mem.fit(setup, name=category)
                self.feature_space[category] = mem
            return True

        except Exception as exc:
            warnings.warn(f"setting inputs was not possible because of Error {exc}!")
            return False

    def set_output(self, output: dict, name: str):

        # ensure variable type
        assert type(output) is dict, "output must be dict and follow the needed structure"

        try:
            mem = Membership()
            mem.fit(output, name=name)
            self.output = mem
            return True

        except Exception as exc:
            warnings.warn(f"Error {exc} occured")
            return False

    def run(self, inputs: dict):
        perception = self._fuzzification(inputs)
        results = self._inference(perception)
        return self._defuzzification(results)


#m = Membership()
#m.fit(accel_crnt, "current acceleration")
#m.get_membership_degree(3)
# m.show()


ruleset = pd.read_csv("experiment/test_rules.csv", sep=";")

fc = FuzzyDistanceController()
fc.set_inputs(settings)
fc.set_ruleset(ruleset)
fc.set_output(accel, "acceleration")
# print(fc.run({"accel_crnt": 3, "target_distance": 100, "vel_crnt": 8.6}))
