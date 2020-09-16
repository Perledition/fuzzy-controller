from matplotlib import pyplot as plt

class Car:

    def __init__(self):
        self.a = 0
        self.v = 0
        self.s = 0
        self.history = {"vel": list(), "t": list(), "acc": list(), "dis": list()}

    def distance(self, t):
        self.s += 0.5 * self.a * (t**2)

    def accelerate(self, final_velocity=0, t=0):
        self.v = final_velocity
        self.a = self.v / t

    def velocity(self, t):
        pass

    def breaking(self):
        pass

    def update(self, final_velocity=0, t=0):
        self.accelerate(final_velocity, t)
        self.distance(t)
        self.history["vel"] += [self.v]
        self.history["acc"] += [self.a]
        self.history["dis"] += [self.s]
        self.history["t"] += [t]

    def get_distance(self):
        return self.s

    def get_velocity(self):
        return self.v

    def get_acceleration(self):
        return f"{self.a} m/s²"


# t = 3 seconds
# final velocity = 50 km/h == 14 m/s

steps = (1, 3, 6)
fv = (1, 14, 14)

c = Car()

vels = list()
index = list()
for step, vel in list(zip(steps, fv)):
    c.update(vel, step)

plt.figure(figsize=(10, 10))

i = 1
for key, values in c.history.items():
    plt.subplot(4, 1, i)
    plt.title(key)
    plt.plot(steps, values)
    i+=1

plt.show()
