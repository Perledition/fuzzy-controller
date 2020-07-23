# import standard modules

# import third party modules
import pandas as pd

# import project related modules
from components.controller.fuzzy import FuzzyDistanceController

df = pd.read_csv("ruleset_fuzzy_distance_controller.csv", index_col=0)
print(df.head())

"""
input:
speed -> what is my current speed
driver type -> how much distance is the driver willing to keep

output: change of distance in m/s


"""

ruleset = pd.read_csv("ruleset_fuzzy_distance_controller.csv", index_col=0)

target_distance = {
    "very low": {"lower_end": 0, "center": 0, "upper_end": 50},
    "low": {"lower_end": 0, "center": 50, "upper_end": 100},
    "medium": {"lower_end": 50, "center": 100, "upper_end": 150},
    "high": {"lower_end": 100, "center": 150, "upper_end": 200},
    "very high": {"lower_end": 150, "center": 200, "upper_end": 200}
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

acceleration = {
    "strong_negative": {"lower_end": -20, "center": -20, "upper_end": -5},
    "negative": {"lower_end": -10, "center": -5, "upper_end": 0},
    "zero": {"lower_end": -5, "center": 0, "upper_end": 5},
    "positive": {"lower_end": 0, "center": 5, "upper_end": 10},
    "strong_positive": {"lower_end": 5, "center": 10, "upper_end": 20},
}

current = {"target_distance": 77, "driver_type": 33, "change_of_distance": 6.3}

fc = FuzzyDistanceController()
fc.set_inputs(settings)
fc.set_ruleset(ruleset)
fc.set_output(acceleration)

print(fc.run(current))