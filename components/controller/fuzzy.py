# import standard modules
import warnings

# import third party modules
import numpy as np
import pandas as pd

# import project related modules
from components.controller.membership import MembershipValidator
from components.controller.activation import PolygonGravity

# TODO: create min_function
# TODO: create center of gravity for absolut -> softmax with weighted average output
# TODO: return value


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
                memberships = self.feature_space[category].get_memberships(value, return_type="dict")
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
                if value > 0:
                    category_members[category].append(key)

        # create a subset of the given rules - copy complete data set and filter afterwards to ensure
        # other memory location and prevent overwriting
        subset = self.rules.loc[:, :]

        # create query conditions and filter the given data set for conditions
        for query in self._query_generator(category_members):
            subset = subset.query(query)

        return subset

    def _inference(self, perception: dict):
        print(perception)

        # filter subset of rules that match the perception - filter because the rest is not needed and can be ignored
        subset = self._get_rule_subset(perception)
        # iterate over the ruleset and check to which degree modus ponens is true
        # TODO: calculate min for each rule

        valid_columns = list(perception.keys())
        for column in valid_columns:

            memberships = perception[column]
            subset[f"{column}_value"] = subset.apply(lambda row: memberships[row[column]], axis=1)

        subset["degree"] = subset.min(axis=1)

        # TODO: think about a solution how to solve the joint value defuzzification

        result = subset.loc[:, ["acceleration", "degree"]].to_dict("r")
        print(result)
        return dict()

    def _defuzzification(self):

        # get_centroid(self, lower_end, upper_end, cut, slope, flat_side=(0, 0))
        pass

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
                self.feature_space[category] = MembershipValidator(setup, category_name=category)
            return True

        except Exception as exc:
            warnings.warn(f"setting inputs was not possible because of Error {exc}!")
            return False

    def set_output(self, output: dict, name: str):

        # ensure variable type
        assert type(output) is dict, "output must be dict and follow the needed structure"

        try:
            self.output = MembershipValidator(output, category_name=name)
            return True

        except Exception as exc:
            warnings.warn(f"Error {exc} occured")
            return False

    def run(self, inputs: dict):
        perception = self._fuzzification(inputs)
        results = self._inference(perception)





