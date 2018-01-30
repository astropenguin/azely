"""Dayplot of the Sun's elevation today."""

import azely
import numpy as np
import matplotlib.pyplot as plt

# calculation
c = azely.Calculator('mitaka')
hr = np.linspace(0, 24, 601) # [0, 24] hr
azel = c('sun', hr) # AzEl object

# plotting
plt.plot(hr, azel.el)
plt.xlim(0, 24)
plt.ylim(0, 90)
plt.title(f'{c.location["name"]} / {c.date}')
plt.xlabel(f'{c.timezone["name"]} (hr)')
plt.ylabel('Elevation (deg)')
plt.show()
