# public items
__all__ = ['dayplot']

# standard library
from collections import OrderedDict
from logging import getLogger
logger = getLogger(__name__)

# dependent packages
import azely
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import CheckButtons


# functions
def dayplot(**kwargs):
    # azel calculator
    c = azely.Calculator(kwargs['location'], kwargs['timezone'], kwargs['date'])
    t = np.linspace(0, 24, 601)
    azels = c(kwargs['objects'], t, squeeze=False)

    # figure settings
    figure, axes = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
    figure.subplots_adjust(0.1, 0.1, 0.8, 0.9, 0.1, 0.2)

    # el-axis settings
    ax_el = axes[0]
    tw_el = ax_el.twinx()
    ax_el.set_xlim([0, 24])
    ax_el.set_ylim([0, 90])
    ax_el.set_xticks(np.arange(24+1))
    ax_el.set_yticks(np.arange(0, 90+1, 10))
    ax_el.set_title(f'{c.location["name"]} / {c.date}')
    ax_el.set_ylabel('Elevation (deg)')
    tw_el.set_yticks(np.arange(0, 90+1, 30))
    tw_el.grid(False)

    # az-axis settings
    ax_az = axes[1]
    tw_az = ax_az.twinx()
    ax_az.set_xlim([0, 24])
    ax_az.set_ylim([0, 360])
    ax_az.set_xticks(np.arange(24+1))
    ax_az.set_yticks(np.arange(0, 360+1, 45))
    ax_az.set_xlabel(f'{c.timezone["name"]} (hr)')
    ax_az.set_ylabel('Azimuth (deg)')
    tw_az.set_yticks(np.arange(0, 360+1, 45))
    tw_az.set_yticklabels(list('N E S W N'))
    tw_az.grid(False)

    # plot az & el
    ls_az = OrderedDict()
    ls_el = OrderedDict()
    for name, azel in azels.items():
        az, el = azel.az.value, azel.el.value
        ma_az = np.hstack([np.abs(np.diff(az))>180, False]) | (el < 0)
        ma_el = (el < 0)
        ls_el[name], = ax_el.plot(t, np.ma.array(el, mask=ma_el), label=name)
        ls_az[name], = ax_az.plot(t, np.ma.array(az, mask=ma_az), label=name)

    # check-buttons settings
    ax_cb = plt.axes([0.85, 0.1, 0.1, 0.8])
    cb = CheckButtons(ax_cb, list(ls_el.keys()), [True]*len(ls_el))
    cc = plt.rcParams['axes.prop_cycle']()

    for line in cb.lines:
        line[0].set_alpha(0.0)
        line[1].set_alpha(0.0)

    for rec, c in zip(cb.rectangles, cc):
        rec.set_facecolor(c['color'])
        rec.set_edgecolor('none')

    def toggle(label):
        index = list(ls_el.keys()).index(label)
        visible = ls_el[label].get_visible()
        ls_el[label].set_visible(not visible)
        ls_az[label].set_visible(not visible)
        cb.rectangles[index].set_alpha(not visible)
        plt.draw()

    cb.on_clicked(toggle)

    # show or save plot
    if kwargs['show']:
        plt.show()
    elif kwargs['save']:
        plt.savefig(f'azely_dayplot.{kwargs["extension"]}')
