# coding: utf-8

"""Day plot of the solar objects' elevations with given date, location, and timezone."""

import azely
import numpy as np
import matplotlib.pyplot as plt

# date and locations
date = '2017-01-01' # optional: None
location = 'ALMA Observatory'
timezone = 'Mitaka' # optional: None, 9.0, 'LST'

# objects
objs = azely.Objects()['Solar']

# calculating and plotting
azel = azely.AzEl(location, timezone, date)
t = np.arange(0, 24.01, 0.01)

for label, obj in objs.items():
    el = azel(obj, t).el
    plt.plot(t, el, label=label)

plt.xlim([0, 24])
plt.ylim([0, 90])
plt.title('{0} / {1}'.format(azel.location['name'], azel.date))
plt.xlabel('{0} (hr)'.format(azel.timezone['timezone_name']))
plt.ylabel('Elevation (deg)')
plt.legend()
plt.show()
