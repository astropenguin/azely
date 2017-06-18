# coding: utf-8

'''Day plot of the Sun's elevation today.'''

import azely
import numpy as np
import matplotlib.pyplot as plt

# calculating
azel = azely.AzEl('Mitaka')
t = np.arange(0, 24, 0.01)
el = azel('Sun', t).el

# plotting
plt.plot(t, el)
plt.xlim([0, 24])
plt.ylim([0, 90])
plt.title(azel['location']['name'])
plt.xlabel(azel['timezone']['timezone_name'])
plt.ylabel('Elevation')
plt.show()
