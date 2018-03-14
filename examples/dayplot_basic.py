"""Dayplot of solar objects' elevations with given date, location, and timezone."""

import azely
import numpy as np
import matplotlib.pyplot as plt

# date and locations
date = '2018-01-01'
location = 'alma observatory'
timezone = 'local sidereal time'

# calculation
calc = azely.Calculator(location, timezone, date)
hr = np.linspace(0, 24, 601)
azels = calc('solar', hr)

# plotting
for azel in azels:
    plt.plot(hr, azel.el, label=azel.info.name)

plt.xlim(0, 24)
plt.ylim(0, 90)
plt.title(f'{calc._location["name"]} / {calc._date}')
plt.xlabel(f'{calc._timezone["name"]} (hr)')
plt.ylabel('Elevation (deg)')
plt.legend()
plt.show()
