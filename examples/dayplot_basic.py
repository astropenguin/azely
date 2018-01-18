# coding: utf-8

"""Day plot of the solar objects' elevations with given date, location, and timezone."""

import azely
import numpy as np
import matplotlib.pyplot as plt

# date and locations
date = '2018-01-01'
location = 'alma observatory'
timezone = 'mitaka'

# calculation
c = azely.Calculator(location, timezone, date)
t = np.linspace(0, 24, 601)
azels = c('Solar', t) # OrderedDict

# plotting
for name, azel in azels.items():
    plt.plot(t, azel.el, label=name)

plt.xlim(0, 24)
plt.ylim(0, 90)
plt.title(f'{c.location["name"]} / {c.date}')
plt.xlabel(f'{c.timezone["timezone_name"]} (hr)')
plt.ylabel('Elevation (deg)')
plt.legend()
plt.show()
