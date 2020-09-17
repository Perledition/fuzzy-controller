# import standard modules

# import third party modules
import numpy as np
import pandas as pd
from matplotlib import pyplot as plt

# import project related modules
from experiment.intervals import accel, settings
from components.vehicle.bidirectional import SimpleCar
from components.controller.fuzzy import FuzzyDistanceController


# define the fuzzy controller configuration
# ruleset = pd.read_csv("ruleset_fuzzy_distance_controller.csv", index_col=0)
ruleset = pd.read_csv("test_rules.csv", sep=";")
print(ruleset.head())

# set fuzzy controller which will be used by the following car
fc = FuzzyDistanceController()
fc.set_inputs(settings)
fc.set_ruleset(ruleset)
fc.set_output(accel, "acceleration")

fc.show_members()

# (meter per seconds, amount of seconds to drive)
route = [
    (8.78, 5), (12.667, 3), (12.667, 4), (17.333, 6), (16.84, 3), (12.222, 2), (6, 5), (0, 5),
    (5.18, 2), (12.23, 3), (16.667, 2), (18.313, 3), (23.333, 2), (26.212, 2), (15, 5), (7, 3), (0, 4)
]


c = SimpleCar()
c.set_route(route=route)

cf = SimpleCar(controller=fc, adoption_rate=0.6)

distance_between = list()
for s in range(0, 60):
    dis_lead_to_follow = c.get_second(s)[2] - cf.distance
    distance_between.append(c.get_second(s)[2] - cf.distance)

    if dis_lead_to_follow > 0:
        print("second: ", s)
        cf.update(dis_lead_to_follow, s)
    else:
        print("crash in sec: ", s)
        cf.update(dis_lead_to_follow, s)

    print("")


# velocity plot
plt.figure(figsize=(10, 15))

plt.subplot(4, 1, 1)

run = 60 # 31# 15 # 31
time = [s for s in range(0, run)]
plt.plot(time, [c.get_second(i)[0] for i in range(0, run)], label="leading car")
plt.plot(time, cf.history["velocity"][:run], label="following car")
plt.plot()
plt.title("Velocity chart")
plt.xlabel("second")
plt.ylabel("[ m/s ]")
plt.legend()


# acceleration plot
plt.subplot(4, 1, 2)
plt.plot(time, [c.get_second(i)[1] for i in range(0, run)], label="leading car")
plt.plot(time, cf.history["acceleration"][:run], label="following car")
plt.title("acceleration chart")
plt.xlabel("second")
plt.ylabel("[ m/s2 ]")
plt.legend()

# distance plot
plt.subplot(4, 1, 3)
plt.plot(time, [c.get_second(i)[2] for i in range(0, run)], label="leading car")
plt.plot(time, cf.history["distance"][:run], label="following car")
plt.title("distance chart")
plt.xlabel("second")
plt.ylabel("[ m ]")
plt.legend()

# distance between vehicles plot
plt.subplot(4, 1, 4)
plt.plot(time, distance_between[:run], c="r")
plt.title("distance between cars chart")
plt.xlabel("second")
plt.ylabel("[ m ]")
plt.tight_layout()
plt.show()