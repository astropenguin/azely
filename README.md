# azely

[![Release](https://img.shields.io/pypi/v/azely?label=Release&color=cornflowerblue&style=flat-square)](https://pypi.org/project/azely/)
[![Python](https://img.shields.io/pypi/pyversions/azely?label=Python&color=cornflowerblue&style=flat-square)](https://pypi.org/project/azely/)
[![Downloads](https://img.shields.io/pypi/dm/azely?label=Downloads&color=cornflowerblue&style=flat-square)](https://pepy.tech/project/azely)
[![DOI](https://img.shields.io/badge/DOI-10.5281/zenodo.3680060-cornflowerblue?style=flat-square)](https://doi.org/10.5281/zenodo.3680060)
[![Tests](https://img.shields.io/github/actions/workflow/status/astropenguin/azely/tests.yaml?label=Tests&style=flat-square)](https://github.com/astropenguin/azely/actions)

Azimuth/elevation calculator for astronomical objects

## Overview

**Azely** (pronounced "as-elie") is a Python package for calculation and plotting of horizontal coordinates (azimuth and elevation) of astronomical objects at given location and time.
While the core calculation and plotting are handled by [Astropy](https://astropy.org) and [Matplotlib](https://matplotlib.org), Azely provides a simple API for easier and more intuitive use.
For example, calculating and plotting the elevation of the Sun in Tokyo for today can be done in a single line:

```python
import azely

azely.calc('Sun', 'Tokyo').el.plot(ylim=(0, 90))
```

![one-liner.svg](https://raw.githubusercontent.com/astropenguin/azely/1.0.0/docs/_static/one-liner.svg)

## Features

- **Simple API:** Just pass query strings for the object, location, and time information to the `azely.calc()` function. The output is a [pandas](https://pandas.pydata.org) DataFrame of the calculated azimuth and elevation, which makes it easy to convert to other formats like CSV or plot with Matplotlib.
- **Information Retrieval and Cache:** Azely automatically fetches object coordinates and location details from online services. The fetched information is cached in a local TOML file for offline use.

## Installation

```shell
pip install azely
```

## Basic Usage

The easiest way to use Azely is to pass query strings for the object, location, and time information to the `azely.calc()` function to get the azimuth/elevation DataFrame:

```python
import azely

df = azely.calc(object, location, time)
```

### Query Specification

Parameter | Format & Description | Examples
--- | --- | ---
`location`| **`''`**: Current location inferred from your IP address (default; not cached). | `''`
`location`| **`'<name>'`**: Name of the location to be searched online. | `'ALMA AOS'`, `'Tokyo'`
`location`| **`'<name>;<longitude>;<latitude>[;altitude]'`**: Full location information (not cached). A dictionary is also accepted. | `'ASTE; -67.70d; -22.97d; 4860m'`, `{'name': 'ASTE', 'longitude': '-67.70d', 'latitude': '-22.97d', 'altitude': '4860m'}`
`object` | **`'<name>'`**: Name of the object to be searched online. | `'Sun'`, `'3C 273'`
`object` | **`'<name>;<longitude>;<latitude>[;<frame>]'`**: Full object information (not cached). A dictionary is also accepted. Frame defaults to `'icrs'`. | `'M42; 5h35m; -5d23m'`, `{'name': 'M42', 'longitude': '5h35m', 'latitude': '-5d23m'}`
`time` | **`''`**: 00:00 today to 00:00 tomorrow at a 10-minute step (default; not cached). Timezone follows given location. | `''`
`time` | **`'[<start>][;<stop>][;<step>][;<timezone>]'`**: Full time information (not cached). A dictionary is also accepted. Omitted parts fall back to defaults (`'00:00 today'`, `'00:00 tomorrow'`, `'10min'`, `''`). Timezone follows given location unless not specified. | `'2025-01-01'`, `'09:00 JST today; in 2 days; 1h'`, `{'start': '09:00 JST today', 'stop': 'in 2 days', 'step': '1h'}`

### DataFrame Example

```python
import azely

df = azely.calc('Sun', 'Tokyo', '2025-07-07 00:00 JST; in 12 hours; 1h')
print(df)
```

```
                                   az         el
JST
2025-07-07 00:00:00+09:00    3.846189 -31.611817
2025-07-07 01:00:00+09:00   19.640291 -29.125374
2025-07-07 02:00:00+09:00   33.835158 -23.630885
2025-07-07 03:00:00+09:00   45.977158 -15.805563
2025-07-07 04:00:00+09:00   56.259606  -6.319155
2025-07-07 05:00:00+09:00   65.148244   4.302369
2025-07-07 06:00:00+09:00   73.166182  15.680605
2025-07-07 07:00:00+09:00   80.862836  27.541537
2025-07-07 08:00:00+09:00   88.925229  39.663496
2025-07-07 09:00:00+09:00   98.525644  51.808030
2025-07-07 10:00:00+09:00  112.475716  63.549892
2025-07-07 11:00:00+09:00  139.635373  73.527391
```

### Plotting Example

```python
import azely
import matplotlib.pyplot as plt

fig, ax = plt.subplots(figsize=(12, 4))

for obj in ('Sun', 'Sgr A*', 'M87', 'M104', 'Cen A'):
    df = azely.calc(obj, 'ALMA AOS', '2017 Apr 11th UTC')
    df.el.plot(ax=ax, label=df.object.name)

ax.set_title(f'Location: {df.location.name}')
ax.set_ylabel('Elevation (deg)')
ax.set_ylim(0, 90)
ax.grid(which='both')
ax.legend()
```

![multiple-objects.svg](https://raw.githubusercontent.com/astropenguin/azely/1.0.0/docs/_static/multiple-objects.svg)

## Advanced Usage

### Local Sidereal Time

Using the `in_lst()` method of the output DataFrame, you can convert its time index to the local sidereal time (LST).
Here is a example script that shows JST on the bottom axis and LST on the top axis:

```python
import azely
import matplotlib.pyplot as plt
from matplotlib.dates import DateFormatter

fig, ax_jst = plt.subplots(figsize=(12, 4))
ax_lst = ax_jst.twiny()

df = azely.calc('Sun', 'Tokyo', '2020-01-01')
df.el.plot(ax=ax_jst, label=df.object.name)
ax_jst.set_title(f'Location: {df.location.name}')
ax_jst.set_ylabel('Elevation (deg)')
ax_jst.set_ylim(0, 90)
ax_jst.grid(which='both')
ax_jst.legend()

# plot invisible elevation for the LST axis
df.in_lst().el.plot(ax=ax_lst, alpha=0)
ax_lst.xaxis.set_major_formatter(DateFormatter('%H:%M'))
ax_jst.margins(0)
ax_lst.margins(0)
```

![lst-axis.svg](https://raw.githubusercontent.com/astropenguin/azely/1.0.0/docs/_static/lst-axis.svg)

### Cache and Custom Information

The fetched location/object/time information is automatically saved to `$XDG_CONFIG_HOME/azely/cache.toml` (or `~/.config/azely/cache.toml`).
You can control this behavior with the `append` and `overwrite` options of `azely.calc()`:

- `append=False` (read-only): Returns the cached information if it exists. If not, fetches new information but **never** adds it to the cache.
- `append=True` (append-only; default): Returns the cached information if it exists. If not, fetches new information and **always** appends it to the cache.
- `overwrite=True` (force-update): Regardless of the existence of the cached information and the value of the `append` option, **always** fetches new information and overwrites the cached information with it.

You can change the source TOML file with the `source` option.
This can be used to create a configuration file with user-defined locations, objects, and times:

```toml
# user.toml

[location.ASTE]
name = "Atacama Submillimeter Telescope Experiment"
longitude = "-67d42m11s"
latitude = "-22d58m18s"
altitude = "4860m"

[object.GC]
name = "Galactic Center"
longitude = "0d0m0s"
latitude = "0d0m0s"
frame = "galactic"

[time.Weekly]
start = "00:00 today"
stop = "in a week"
step = "1h"
```

```python
import azely

df = azely.calc('GC', 'ASTE', 'Weekly', source='user.toml')
print(df)
```

```
                                   az         el
America/Santiago
2025-07-06 00:00:00-04:00  233.966638  79.305274
2025-07-06 01:00:00-04:00  249.765199  66.864731
2025-07-06 02:00:00-04:00  251.885356  53.751800
2025-07-06 03:00:00-04:00  250.791907  40.619356
2025-07-06 04:00:00-04:00  248.196309  27.641160
...                               ...        ...
2025-07-12 19:00:00-04:00  109.691832  37.638970
2025-07-12 20:00:00-04:00  108.182993  50.748158
2025-07-12 21:00:00-04:00  109.245142  63.889110
2025-07-12 22:00:00-04:00  119.352834  76.638576
2025-07-12 23:00:00-04:00  194.243652  83.824660

[168 rows x 2 columns]
```

## Migration Guide from 0.7.0 to 1.0.0

Azely version 1.0.0 includes several breaking changes.
If you are migrating from Azely version 0.7.0, please check the following changes.

### The main function and its options have been renamed.

- **0.7.0:** `azely.compute(object, site, time, view)`
- **1.0.0:** `azely.calc(object, location, time)`
    - The `site` options has been renamed to `location`.
    - The `view` option has been removed. The timezone is inferred from the `location` or can be specified within the `time`.
    - The default value settings via `config.toml` has been removed.

###  The `in_lst` property of the output DataFrame has become a method.

- **0.7.0:** `df.in_lst` (and `df.in_utc`)
- **1.0.0:** `df.in_lst()` (and `df.in_utc()`)

### The information cache has been totally changed.

- The separate cache TOML files (`objects.toml`, `locations.toml`) are now merged into a single `cache.toml`.
- The new `overwrite` option force-updates cached information instead of appending `'!'` to the query string.
- The new `append` and `source` options provide finer control over the cache behavior.
