# coding: utf-8

'''Day plot of the solar objects' elevations with given date, location, and timezone.'''

import azely
import numpy as np
import matplotlib.pyplot as plt

date = '2017.05.15' # optional: None

# locations
locs = azely.Locations(date)
observer = locs['alma observatory']
timezone = locs['japan'] # optional: None, 'LST'

# objects
objs = azely.ObjectLists()['solar']

# calculating and plotting
calc = azely.AzEl(observer, timezone, date)
t = np.arange(0, 24, 0.01)

for name, obj in objs.items():
    el = calc(obj, t).El
    plt.plot(t, el, label=name)

plt.xlim([0, 24])
plt.ylim([0, 90])
plt.title(observer['name'])
plt.xlabel(timezone['timezone_name'])
plt.ylabel('Elevation')
plt.legend()
plt.show()
