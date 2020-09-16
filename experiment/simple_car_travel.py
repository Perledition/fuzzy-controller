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
ruleset = pd.read_csv("ruleset_fuzzy_distance_controller.csv", index_col=0)

fc = FuzzyDistanceController()
fc.set_inputs(settings)
fc.set_ruleset(ruleset)
fc.set_output(accel, "acceleration")

# (meter per seconds, amount of seconds to drive)
route = [(27.78, 5), (16.667, 3), (16.667, 4), (33.333, 6), (33.333, 3), (22.222, 2), (0, 5), (0, 5)]

c = SimpleCar()
c.set_route(route=route)

cf = SimpleCar(controller=fc)
for s in range(0, 31):
    dis_lead_to_follow = c.get_second(s)[2] - cf.distance
    if dis_lead_to_follow > 0:
        print("distance_between cars: ", dis_lead_to_follow)
        cf.update(dis_lead_to_follow)
    else:
        print("crash in sec: ", s)


# velocity plot
plt.figure(figsize=(10, 15))

plt.subplot(3, 1, 1)

run = 15 # 31
time = [s for s in range(0, run)]
plt.plot(time, [c.get_second(i)[0] for i in range(0, run)])
plt.plot(time, cf.history["velocity"][:run])
plt.plot()
plt.title("Velocity chart")
plt.xlabel("second")
plt.ylabel("[ m/s ]")


# acceleration plot
plt.subplot(3, 1, 2)
plt.plot(time, [c.get_second(i)[1] for i in range(0, run)])
plt.plot(time, cf.history["acceleration"][:run])
plt.title("acceleration chart")
plt.xlabel("second")
plt.ylabel("[ m/s2 ]")

# distance plot
plt.subplot(3, 1, 3)
plt.plot(time, [c.get_second(i)[2] for i in range(0, run)])
plt.plot(time, cf.history["distance"][:run])
plt.title("distance chart")
plt.xlabel("second")
plt.ylabel("[ m ]")

plt.show()