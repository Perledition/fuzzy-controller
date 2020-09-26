# import standard modules

# import third party modules
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# import project related modules
from experiment.intervals import accel, settings
from components.vehicle.bidirectional import SimpleCar
from components.controller.fuzzy import FuzzyController

##############################################
# define the fuzzy controller configuration  #
##############################################

# read in the rule set which is used to determine the resulting action at a certain behaviour tendency
ruleset = pd.read_csv("test_rules.csv", sep=";")
print(ruleset.head())

# set fuzzy controller which will be used by the following car
# at this point we already hand over the parameter definitions and the ruleset, since it is easier to follow the
# pure controller logic this way
fc = FuzzyController()

# hand over settings which is imported from experiments.intervals.py and contains a dict with all used parameters
fc.set_inputs(settings)

# hand over the rule set as pandas data frame which was created above from the predefined csv rule set
fc.set_ruleset(ruleset)

# handover the output parameter, in order to let the controller find the proper reaction to a given situation
fc.set_output(accel, "acceleration")

# just plot the members / parameters of the current controller, which helps to see if the controller did a proper job
# on initialization
fc.show_members()


##############################################
#      set up the experiment environment     #
##############################################

# define the milestones or steps the leading car will drive. The route must be predefined for this experiment
# the total duration of the experiment is defined by the sum of seconds to hold velocity of all tuples (milestones)
# (meter per seconds, amount of seconds to hold desired velocity)
route = [
    (8.78, 5), (12.667, 3), (12.667, 4), (17.333, 6), (16.84, 3), (12.222, 2), (6, 5), (0, 5),
    (5.18, 2), (12.23, 3), (16.667, 2), (18.313, 3), (23.333, 2), (26.212, 2), (15, 5), (7, 3), (0, 4)
]

# initialize the leading car which will get the predefined route from above
c = SimpleCar()
c.set_route(route=route)

# initialize the following car which will get no route but the controller from the beginning
# it gets also an adoption rate which can be seen as percentage value
# how strong the car will apply the recommendation of the fuzzy controller
cf = SimpleCar(controller=fc, adoption_rate=0.6)


##############################################
#                 experiment                 #
##############################################

# initialize an empty list to keep track of the distance between the cars
distance_between = list()

# for each second of the experiment duration of one minute run the following steps
for s in range(0, 60):

    # the the distance between the cars - in a real world this would be done by a radar or a laser system
    # in this simple case we need to calculate hand hand it over to the following car since we do not have
    # a radar system in place
    dis_lead_to_follow = c.get_second(s)[2] - cf.distance
    distance_between.append(c.get_second(s)[2] - cf.distance)

    # in case the distance is greater than zero print the second and run the update for the following car
    # otherwise print crash and second and run the update anyways.
    # the update takes only the current second and the distance between cars, since current velocity and current
    # acceleration are defined by the following car itself.
    # for the leading car no update is needed since we handed over the route at initialization and the complete
    # route and the behavior was pre calculated.
    if dis_lead_to_follow > 0:
        print("second: ", s)
        cf.update(dis_lead_to_follow, s)
    else:
        print("crash in sec: ", s)
        cf.update(dis_lead_to_follow, s)

    print("")


##############################################
#               Show results                 #
##############################################
# velocity plot
plt.figure(figsize=(10, 15))

plt.subplot(4, 1, 1)

# run defines the duration of the experiment
run = 60

# show velocity at a given second for both cars
time = [s for s in range(0, run)]
plt.plot(time, [c.get_second(i)[0] for i in range(0, run)], label="leading car")
plt.plot(time, cf.history["velocity"][:run], label="following car")
plt.plot()
plt.title("Velocity chart")
plt.xlabel("second")
plt.ylabel("[ m/s ]")
plt.legend()


# show acceleration at a given second for both cars
plt.subplot(4, 1, 2)
plt.plot(time, [c.get_second(i)[1] for i in range(0, run)], label="leading car")
plt.plot(time, cf.history["acceleration"][:run], label="following car")
plt.title("acceleration chart")
plt.xlabel("second")
plt.ylabel("[ m/s2 ]")
plt.legend()

# show archived distance at a given second for both cars
plt.subplot(4, 1, 3)
plt.plot(time, [c.get_second(i)[2] for i in range(0, run)], label="leading car")
plt.plot(time, cf.history["distance"][:run], label="following car")
plt.title("distance chart")
plt.xlabel("second")
plt.ylabel("[ m ]")
plt.legend()

# show the distance between both cars at a given second
plt.subplot(4, 1, 4)
plt.plot(time, distance_between[:run], c="r")
plt.title("distance between cars chart")
plt.xlabel("second")
plt.ylabel("[ m ]")
plt.tight_layout()
plt.show()