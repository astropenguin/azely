# coding: utf-8

'''Day plot of the Sun's elevation today.'''

import azely
import numpy as np
import matplotlib.pyplot as plt

# locations
observer = azely.Locations()['mitaka']

# calculating
calc = azely.AzEl(observer)
t = np.arange(0, 24, 0.01)
el = calc('Sun', t).El

# plotting
plt.plot(t, el)
plt.xlim([0, 24])
plt.ylim([0, 90])
plt.title(observer['name'])
plt.xlabel(observer['timezone_name'])
plt.ylabel('Elevation')
plt.show()
