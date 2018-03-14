"""Dayplot of the Sun's elevation today."""

import azely
import numpy as np
import matplotlib.pyplot as plt

# calculation
calc = azely.Calculator('mitaka')
hr = np.linspace(0, 24, 601)
azel = calc('sun', hr)

# plotting
plt.plot(hr, azel.el, label=azel.info.name)
plt.xlim(0, 24)
plt.ylim(0, 90)
plt.title(f'{calc._location["name"]} / {calc._date}')
plt.xlabel(f'{calc._timezone["name"]} (hr)')
plt.ylabel('Elevation (deg)')
plt.show()
