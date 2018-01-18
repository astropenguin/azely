# coding: utf-8

"""Day plot of the Sun's elevation today."""

import azely
import numpy as np
import matplotlib.pyplot as plt

# calculation
c = azely.Calculator('mitaka')
t = np.linspace(0, 24, 200)
azel = c('Sun', t).el # AzEl object

# plotting
plt.plot(t, azel.el)
plt.xlim(0, 24)
plt.ylim(0, 90)
plt.title(f'{c.location["name"]} / {c.date}')
plt.xlabel(f'{c.timezone["timezone_name"]} (hr)')
plt.ylabel('Elevation (deg)')
plt.show()
