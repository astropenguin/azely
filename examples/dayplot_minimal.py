"""Dayplot of the Sun's elevation today."""

import azely
import numpy as np
import matplotlib.pyplot as plt

# calculation
c = azely.Calculator('mitaka')
t = np.linspace(0, 24, 601)
azel = c('sun', t) # AzEl object

# plotting
plt.plot(t, azel.el)
plt.xlim(0, 24)
plt.ylim(0, 90)
plt.title(f'{c.location["name"]} / {c.date}')
plt.xlabel(f'{c.timezone["name"]} (hr)')
plt.ylabel('Elevation (deg)')
plt.show()
