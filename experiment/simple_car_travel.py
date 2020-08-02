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


def get_status(car, index=0, lead=False):
    if lead is False:
        print(f"{index} Car2 a: {car.acceleration}, v: {car.velocity}, d: {car.distance}, td: {car.distance_lead}")
    else:
        print(f"{index} Car1 a: {car.acceleration}, v: {car.velocity}, d: {car.distance}")

# leading car milestones
# experiment for a duration of 20 seconds
# define x scalar for seconds the test runs
seconds = [s for s in range(1, 60)]
milestones = [2, 3, 5, 6, 9, 10, 20, 19, 18, 15,
              12, 18, 20, 16, 19, 18, 10, 5, 4, 1,
              2, 5, 10, 12, 5, 6, 4, 5, 4, 1,
              2, 3, 5, 12, 19, 18, 10, 10, 10, 10,
              12, 18, 20, 16, 19, 18, 10, 5, 4, 6,
              7, 9, 15, 16, 19, 18, 10, 3, 6, 1,
              ]

milestones = list(zip(seconds, milestones))


car_lead = SimpleCar(milestones)
car_follow = SimpleCar(controller=fc, distance_lead=10)


# print("nodes", len(nodes))

for sec in seconds:
    car_lead.update(sec)
    get_status(car_lead, sec, lead=True)
    car_follow.update(sec, car_lead.distance)
    get_status(car_follow, sec)


def plot_test(car1, car2):

    # define the size of figure
    plt.figure(figsize=(10, 10))

    # get all parameters of the car which need to be plotted
    parameters = list(car2.blackbox.keys())
    plt_size = len(parameters)

    # iterate over all parameters but ignore target distance for now
    # since target distance will only be available for the following car
    for ix, p in enumerate(parameters):
        if p != "target_distance":

            # create a subplot for each parameter and compare car1 with car2
            plt.subplot(plt_size, 1, ix+1)
            plt.plot(seconds, car1.blackbox[p], label=f"leading car {p}")
            plt.plot(seconds, car2.blackbox[p], label=f"following car {p}")
            plt.xticks(np.arange(0, len(seconds), 1))
            plt.legend(loc="upper left")
            plt.grid()

    # define a last plot for the target distance
    plt.subplot(plt_size, 1, plt_size)
    plt.plot(seconds, car2.blackbox["target_distance"], label="distance between cars")
    plt.plot(seconds, [car2.distance_prev for _ in seconds], label="prev_distance")
    plt.xticks(np.arange(0, len(seconds), 1))
    plt.legend(loc="upper left")
    plt.grid()
    plt.show()


plot_test(car_lead, car_follow)

