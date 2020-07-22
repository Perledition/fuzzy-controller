# import standard modules
import warnings

# import third party modules
import numpy as np
import pandas as pd

# import project related modules
from components.controller.membership import MembershipValidator

# TODO: add input values
# TODO: add ruleset
# TODO: create min_function
# TODO: create center of gravity for absolut -> softmax with weighted average output
# TODO: return value


class FuzzyDistanceController(object):

    def __init__(self):

        # feature space / inputs to measure memberships
        self.feature_space = dict()

        # rule set applied for inference
        self.rules = None

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

    def _inference(self, perception):
        return dict()

    def _defuzzification(self):
        pass

    def add_ruleset(self, rules: pd.DataFrame):
        pass

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

    def set_output(self):
        pass

    def run(self, inputs: dict):
        perception = self._fuzzification(inputs)
        results = self._inference(perception)



"""
input:
speed -> what is my current speed
driver type -> how much distance is the driver willing to keep

output: change of distance in m/s


"""

target_distance = {
    "very_low": {"lower_end": 0, "center": 0, "upper_end": 50},
    "low": {"lower_end": 0, "center": 50, "upper_end": 100},
    "medium": {"lower_end": 50, "center": 100, "upper_end": 150},
    "high": {"lower_end": 100, "center": 150, "upper_end": 200},
    "very_high": {"lower_end": 150, "center": 200, "upper_end": 200}
}

driver_type = {
    "aggressive": {"lower_end": 0, "center": 0, "upper_end": 50},
    "medium": {"lower_end": 25, "center": 50, "upper_end": 75},
    "defensive": {"lower_end": 50, "center": 75, "upper_end": 100}
}

change_of_distance = {
    "strong_negative": {"lower_end": -20, "center": -20, "upper_end": -5},
    "negative": {"lower_end": -10, "center": -5, "upper_end": 0},
    "zero": {"lower_end": -5, "center": 0, "upper_end": 5},
    "positive": {"lower_end": 0, "center": 5, "upper_end": 10},
    "strong_positive": {"lower_end": 5, "center": 10, "upper_end": 20},
}

settings = {
    "target_distance": target_distance,
    "driver_type": driver_type,
    "change_of_distance": change_of_distance
 }

current = {"target_distance": 34, "driver_type": 33, "change_of_distance": 6.3}

fc = FuzzyDistanceController()
fc.set_inputs(settings)
print(fc.run(current))

# td = MembershipValidator(target_distance)
# dt = MembershipValidator(driver_type)
# cod = MembershipValidator(change_of_distance)

# current = (5, 40, 17.5)

# print(td.max, td.min)
# print(td.category)
# print(td.get_memberships(5, return_type="dict"))
# print(dt.get_memberships(40, return_type="dict"))
# print(cod.get_memberships(17.5, return_type="dict"))

