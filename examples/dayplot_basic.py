# coding: utf-8

'''Day plot of the solar objects' elevations with given date, location, and timezone.'''

import azely
import numpy as np
import matplotlib.pyplot as plt


# date and locations
date = '2017.05.15' # optional: None
location = 'alma observatory'
timezone = 'japan' # optional: None, 9.0, 'LST'

# objects
objs = azely.Objects()['solar']

# calculating and plotting
azel = azely.AzEl(location, timezone, date)
t = np.arange(0, 24, 0.01)

for name, obj in objs.items():
    el = azel(obj, t).el
    plt.plot(t, el, label=name)

plt.xlim([0, 24])
plt.ylim([0, 90])
plt.title(azel['location']['name'])
plt.xlabel(azel['timezone']['timezone_name'])
plt.ylabel('Elevation')
plt.legend()
plt.show()
