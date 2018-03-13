# public items
__all__ = ['plot_azel',
           'list_azel']

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
def plot_azel(args):
    if isinstance(args.objects, list):
        args.objects = ' '.join(args.objects)

    if isinstance(args.location, list):
        args.location = ' '.join(args.location)

    if isinstance(args.timezone, list):
        args.timezone = ' '.join(args.timezone)

    objects = args.objects
    location = args.location
    timezone = args.timezone
    date = args.date
    filename = args.filename

    # calculate azimuth/elevation
    calc = azely.Calculator(location, timezone, date)
    hr = np.linspace(0, 24, 601)
    azels = calc(objects, hr, unpack_one=False)

    # figure settings
    fig, axes = plt.subplots(2, 1, figsize=(10, 5), sharex=True)
    fig.subplots_adjust(0.1, 0.1, 0.8, 0.9, 0.1, 0.2)

    # el-axis settings
    ax_el = axes[0]
    tw_el = ax_el.twinx()
    ax_el.set_xlim([0, 24])
    ax_el.set_ylim([0, 90])
    ax_el.set_xticks(np.arange(24+1))
    ax_el.set_yticks(np.arange(0, 90+1, 10))
    ax_el.set_title(f'{calc._location["name"]} / {calc._date}')
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
    ax_az.set_xlabel(f'{calc._timezone["name"]} (hr)')
    ax_az.set_ylabel('Azimuth (deg)')
    tw_az.set_yticks(np.arange(0, 360+1, 45))
    tw_az.set_yticklabels(list('N E S W N'))
    tw_az.grid(False)

    # plot azimuth/elevation
    lp_az = OrderedDict() # for azimuth line plots
    lp_el = OrderedDict() # for elevation line plots

    for azel in azels:
        name = azel.info.name
        az = azel.az.value
        el = azel.el.value
        ma_el = (el < 0)
        ma_az = np.hstack([np.abs(np.diff(az))>180, False])
        az = np.ma.array(az, mask=ma_az|ma_el)
        el = np.ma.array(el, mask=ma_el)
        lp_az[name], = ax_az.plot(hr, az, label=name)
        lp_el[name], = ax_el.plot(hr, el, label=name)

    # check-buttons settings
    ax_cb = plt.axes([0.85, 0.1, 0.1, 0.8])
    cb = CheckButtons(ax_cb, list(lp_el), [True]*len(lp_el))
    cc = plt.rcParams['axes.prop_cycle']()

    for line in cb.lines:
        line[0].set_alpha(0.0)
        line[1].set_alpha(0.0)

    for rec, c in zip(cb.rectangles, cc):
        rec.set_facecolor(c['color'])
        rec.set_edgecolor('none')

    def toggle(name):
        index = list(lp_el.keys()).index(name)
        visible = lp_el[name].get_visible()
        lp_el[name].set_visible(not visible)
        lp_az[name].set_visible(not visible)
        cb.rectangles[index].set_alpha(not visible)
        plt.draw()

    cb.on_clicked(toggle)

    # show or save plot
    if filename is None:
        plt.show()
    else:
        plt.savefig(filename)


def list_azel(args):
    pass
