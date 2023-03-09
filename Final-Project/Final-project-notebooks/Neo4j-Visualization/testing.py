import matplotlib.pyplot as plt
from matplotlib import patches
import numpy as np 

xpoints = np.array([0, 6])
ypoints = np.array([0, 250])

draw_circle = patches.Circle((0.5,0.5), 0.3)

figure, axes = plt.subplots()

axes.add_artist(draw_circle)
plt.plot(np.array([0.5,0]), np.array([0.5,0]))
plt.show()