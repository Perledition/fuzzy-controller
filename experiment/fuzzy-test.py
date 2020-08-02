# import standard modules

# import third party modules
import pandas as pd

# import project related modules
from .intervals import accel, settings
from components.controller.fuzzy import FuzzyDistanceController

#########################
# FUZZY CONTROLLER TEST #
#########################

# read in the fuzzy rule set
ruleset = pd.read_csv("ruleset_fuzzy_distance_controller.csv", index_col=0)

# define the current input for the fuzzy controller
current = {"target_distance": 20, "driver_type": 3, "change_of_distance": 16}

# initialize the controller and test a input object
fc = FuzzyDistanceController()
fc.set_inputs(settings)
fc.set_ruleset(ruleset)
fc.set_output(accel, "acceleration")

print(fc.run(current))
