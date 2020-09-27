# import standard modules
import warnings

# import third party modules
import pandas as pd

from matplotlib import pyplot as plt
from shapely.geometry import Polygon
from shapely.geometry import LineString

# import project related modules
from components.controller.membership import Membership


class FuzzyController(object):
    """
    a fuzzy controller for various use cases. The settings of the controller define how precise it can work and what to
    in and output. For a general introduction how to use the class properly read the README.md file
    (chapter: How use the Controller for Your own Experiment -> Usage ). The class provides the functionality of

        1. Fuzzification
        2. interference
        3. Defuzzification

    which can be called by the main function "run".
    """

    def __init__(self):
        self.feature_space = None      # feature space / inputs to measure memberships
        self.rules = None              # rule set applied for inference
        self.output = None             # output space defined by user - needs to follow the same structure as input

    def _fuzzification(self, conditions: dict):
        """
        class internal function which executes the first step for each fuzzy controller request. It will will calculate
        the degree to which each sub group / member of a certain parameter is true. Therefore it will get the y value of
        a members triangle for a given x value for the parameter handed over with the input parameter conditions.
        This degree get calculated for each each input parameter in conditions and each member / subgroup of one
        parameter.

        :param conditions: dict: contains the name of the parameter as key e.g: "vel_crnt" and it's input value e.g 12
                                 name and scale of the condition are defined in the previous settings handed over.

        :return: dict: returns a structure with all condition parameters and it's degrees of "truth"
                       for each sub group / member
        """

        # initialize empty dict as fallback return value
        perception = dict()

        try:
            # calculate the memberships for each category and make them available in dict structure for further process.
            for category, value in conditions.items():

                # request the member ship degree from the previous initialized Class available in the dict
                # for more information read the inline code of set inputs. self.feature_space[category] holds
                # a specific helper class for a input parameter which provides the function get_membership_degree.
                memberships = self.feature_space[category].get_membership_degree(value)
                perception[category] = memberships

            # return dict in structure {"category_name": {"member": membership_confidence, ....}}
            return perception

        except (TypeError, KeyError) as exc:
            warnings.warn("fuzzification was not successfull, make sure your inputs match your settings")
            return dict()

    @staticmethod
    def _query_generator(category_members: dict):
        """
        class specific generator function without influence of class attributes. I will generate a query condition
        from a category name e.g. "vel_crnt" and a membership e.g. "very slow".  -> "vel_crnt" == "very slow".

        :param category_members: dict: holds input parameter names with a member. Example above.

        :return: str: returns a query string
        """
        # generate a query value combinations from category and related values - is needed to keep the query dynamic
        for cat, members in category_members.items():

            # query string must include a [OR  | ] condition - since a category can have multiple members true
            # to a certain degree
            query_string = " | ".join(f"({cat}=='{mem}')" for mem in members)
            yield query_string

    def _get_rule_subset(self, perception: dict):
        """
        class internal function which will filter the rule set of the controller to a useful subset of rules.
        Not all rules will be important for a certain input situation, and therefore this function will limit
        the used ruleset only to the relevant rules from the handed over rule set. For more information how the rule
        set is handed over read the function set_ruleset.

        :param perception: dict: should be the resulting dict structure from the _fuzzification function

        :return: pd.DataFrame: results a pandas data frame filtered to the relevant rules from the ruleset
        """

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

        # use the query list generated and create a final main query with an AND condition between all queries
        # and return the filtered subset.
        return subset.query("&".join(f"({qy})" for qy in q))

    def _inference(self, perception: dict):
        """
        class internal function which takes the results from the fuzzification step and reasonable reactions to
        a given situation (perception). In order to find these possible responses the ruleset is used.

        :param perception: dict: should be the resulting dict structure from the _fuzzification function
        :return: list: returns a list of reactions (dicts) for the output category with degree of truth
        """

        # filter subset of rules that match the perception - filter because the rest is not needed and can be ignored
        subset = self._get_rule_subset(perception)

        # get interval relevant columns - with the name of memberships
        valid_columns = list(perception.keys())
        for column in valid_columns:

            # add the degree of truth to each category from the perception (new column)
            memberships = perception[column]
            subset[f"{column}_value"] = subset.apply(lambda row: memberships[row[column]]["degree"], axis=1)

        # since each member / input parameter has it's own degree calculate the average over all input parameters
        # to get an idea of how true the combination of input parameters is
        subset["degree"] = subset.loc[:, [f"{column}_value" for column in valid_columns]].sum(axis='columns') / len(
            valid_columns)

        # create a set of fuzzy outputs [{"output category": "member", "degree": value of degree}, ...]
        result = subset.loc[:, ["acceleration", "degree"]].to_dict("r")
        return result

    @staticmethod
    def _get_intersection(a: tuple, b: tuple, c: tuple, d: tuple):
        """
        class internal function without influence on class attributes. Calculates the intersection point
        of two vectors.

        :param a: tuple: (x, y) coordinates starting point vector 1
        :param b: tuple: (x, y) coordinates end point vector 1
        :param c: tuple: (x, y) coordinates starting point vector 2
        :param d: tuple: (x, y) coordinates end point vector 2

        :return: tuple: returns (x, y) of intersection
        """

        # create vector from two points for vector 1 and vector 2
        line1 = LineString([a, b])
        line2 = LineString([c, d])

        # calculate the intersection and return tuple - module shapely used for the calculation
        int_pt = line1.intersection(line2)
        point_of_intersection = int_pt.x, int_pt.y
        return point_of_intersection

    @staticmethod
    def _coordinate_validation(x: tuple, y: tuple):
        """
        class internal function without influence on class attributes. check whether a y coordinate must be zero or 1.
        In case the center and the starting or endpoint are equal the y must be zero or one. check input parameter
        definition _meta groups in case the logic is not clear without image.

        :param x: tuple: all x values so from input parameter definition dict lower_end, center, upper_end
        :param y: all y coordinates. values must be binary so either 1 or 0

        :return: tuple: returns tuples with x and y values - y values might be modified
        """

        if (x[0] == x[1]) and (y[0] == y[1]):
            y[0] = 0

        elif (x[1] == x[2]) and (y[1] == y[2]):
            y[1] = 0

        return x, y

    def _member_centroid_generator(self, fuzzy_results: list):
        """
        class internal function which adds the centroid data to each result within fuzzy results. The centroid is
        based on a polygon for each member which results from the members triangle cut by a vector on the height
        of degree. all polygons are based on the output categories from the output parameter set in set_output.

        :param fuzzy_results: list: output of _interference [{"output category": "member", "degree": value of degree}.]
        :return: list: same structure as input but each dict enriched with centroid data
        """

        # initialize empty list which will replace fuzzy_results later
        results = list()

        # loop over each dict in fuzzy_results list in order to add the centroid data to each output category
        for f_set in fuzzy_results:

            # set variables - member name and degree to which the member is true
            member = f_set[self.output.name]
            degree = f_set["degree"]

            # get_member is a function provided by a helper class defined in membership.py
            # for more information read also set_inputs function
            coordinates = self.output.get_member(member)["coordinates"]

            # create polygon coordinates in order to calculate centroid for group
            x = coordinates["x"]
            y = coordinates["y"]

            si = 0
            if x[1] == x[2]:
                si = 1

            x, y = self._coordinate_validation(x, y)
            x1 = (x[0], y[0])

            # get the intersection values from the triangle and the vector of degree
            x2 = self._get_intersection(x1, (x[1 + si], y[1 + si]), (x[0], degree), (x[2], degree))
            x3 = self._get_intersection((x[1], y[1]), (x[2], y[2]), (x[0], degree), (x[2], degree))
            x4 = (x[2], y[2])

            # calculate the centroid for the polygon generated by a certain confidence degree
            poly = Polygon([x1, x2, x3, x4])

            # recreate dict with additional centroid information and add it to output list / array
            results.append({"member": member, "degree": degree, "centroid": tuple(poly.centroid.coords)[0]})

        return results

    def _defuzzification(self, fuzzy_results: list):
        """
        class internal function to perform the final step of defuzzification of the interference results.
        It will create a concrete output value on the x axis of the output parameter. e.g. Acceleration group slow
        goes from 0 to 1. The output value on the x axis will be the centroids x value of the polygon area with the
        polygon area defined by the group "slow" and a vector of degree.

        :param fuzzy_results: list: output of _interference [{"output category": "member", "degree": value of degree}.]
        :return: returns an absolute action value for the output parameter e.g. +0.54 acceleration
        """

        # get the centroid of each member area, to make the output area usable as absolute value
        centroid_data = self._member_centroid_generator(fuzzy_results)

        # create an action value from the center of gravities
        action = 0
        for result in centroid_data:
            try:
                # in case the degree is not 0 (and therefore the area of the polygon is zero as well)
                # add the centroid x value of each member and sub group to it's degree to the action value
                if result["degree"] != 0:
                    action += result["degree"] * result["centroid"][0]

            except ZeroDivisionError:
                continue

        return action

    def set_ruleset(self, rules: pd.DataFrame):
        """
        function to set a rule set and to assign the ruleset to the class attributes.

        :param rules: pandas.DataFrame: rule set which includes all parameters set in set_inputs and set_output

        :return: boolean: True is assignment was successful, False otherwise
        """

        # set self.rules (required rule set) if object type is a pandas data frame: data frame is used to make
        # the code more readable and understandable
        if type(rules) is pd.DataFrame:
            self.rules = rules
            return True
        else:
            return False

    def set_inputs(self, feature_space: dict):
        """
        function initialize a set of parameters as feature space used for calculations.

        :param feature_space: dict: is a setting dict - settings = {
                                                            "name of parameter1": [parameter1, "[ unit of measure]"],
                                                            "name of parameter n": [parameter_n, "[ unit of measure]"],
                                                        }

        :return: boolean: if assignment was successful True, False otherwise
        """

        # ensure empty feature_space - edge case
        self.feature_space = dict()
        try:

            # create a Membership object for each category - the object calculates the memberships
            # the objects will be stored in self.feature_space
            for category, setup in feature_space.items():
                assert type(setup[0]) is dict, f"{category} does not contain a setup dict, create a dict"

                # measure defines the base unit of measure for the groups it will be empty be default
                if len(setup) > 1:
                    measure = setup[1]
                else:
                    measure = ""

                # initialize the class object with it's measure
                mem = Membership(measure=measure)
                mem.fit(setup[0], name=category)

                # store the object in the feature space dict
                self.feature_space[category] = mem
            return True

        except Exception as exc:
            warnings.warn(f"setting inputs was not possible because of Error {exc}!")
            return False

    def set_output(self, output: dict, name: str):
        """
        Sets an output parameter of memberships or sub groups.

        :param output: dict: e.g. output = {"very small": {"lower_end": value of lower end, "center": value of center,
                                                           "upper_end": value of upper end}, "small": { ...
                                            }
                            For more information check README.md or check experiment
        :param name: str: name of the output category
        :return: boolean: True if assignment was successful, False otherwise
        """

        # ensure variable type
        assert type(output) is dict, "output must be dict and follow the needed structure"

        try:
            # create a Membership object which will handle Parameter specific tasks
            # Class Membership can be found in memberships.py
            mem = Membership()
            mem.fit(output, name=name)
            self.output = mem
            return True

        except Exception as exc:
            warnings.warn(f"Error {exc} occured")
            return False

    def show_members(self):
        """
        Function displays the all input parameter set with ser_inputs.

        :return: None: displays plot
        """
        plt.figure(figsize=(10, 15))

        # iterate over each Membership object in feature_space
        for group, config in self.feature_space.items():

            ix = list(self.feature_space.keys()).index(group)
            plt.subplot(len(list(self.feature_space.keys())), 1, ix+1)

            # plot each category / member of one membership object and plot it's triangle
            for category, values in config.memberships.items():
                plt.plot(values["coordinates"]["x"], values["coordinates"]["y"], label=category)

            plt.title(config.name)
            plt.xlabel(config.measure)
            plt.legend()

        plt.tight_layout()
        plt.show()

    def run(self, inputs: dict):
        """
        Main function of the FuzzyController class. It will calculate a response for a given input situation.

        :param inputs: dict: contains key name of each input parameter and an absolute value for each input parameter
        :return: float: returns the absolute reaction value
        """
        perception = self._fuzzification(inputs)
        results = self._inference(perception)
        return self._defuzzification(results)