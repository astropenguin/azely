# Azely

[![PyPI](https://img.shields.io/pypi/v/azely.svg?label=PyPI&style=flat-square)](https://pypi.org/pypi/azely/)
[![Python](https://img.shields.io/pypi/pyversions/azely.svg?label=Python&color=yellow&style=flat-square)](https://pypi.org/pypi/azely/)
[![Test](https://img.shields.io/github/workflow/status/astropenguin/azely/Test?logo=github&label=Test&style=flat-square)](https://github.com/astropenguin/azely/actions)
[![License](https://img.shields.io/badge/license-MIT-blue.svg?label=License&style=flat-square)](LICENSE)

:zap: Computation and plotting of astronomical object's azimuth/elevation

## TL;DR

Azely (pronounced as "as-elie") is a Python package for computation and plotting of horizontal coordinates (azimuth and elevation) of astronomical objects at given location and time.
While computation and plotting are realized by [astropy] and [matplotlib], what Azely provides is high-level API to use them easily.
In fact Azely offers one-liner to compute and plot, for example, one-day elevation of the Sun:

```python
>>> azely.compute('Sun', 'ALMA AOS', '2020-01-01').el.plot(ylim=(0, 90))
```

## Features

- **High-level API:** Azely provides a simple yet powerful `compute()` function. Users can complete most of operation with it (e.g., information acquisition and computation).
- **Handy output:** Azely's output (from `compute()`) is [pandas] DataFrame, a de facto standard data structure of Python. Users can convert it to other formats like CSV and plot it by [matplotlib] using builtin methods.
- **Web information acquisition:** Azely can automatically acquire object and location information (i.e., longitude and latitude) from online services (e.g., catalogues or maps). Obtained information is cached in a local [TOML] file for an offline use.
- **User-defined information:** Azely also offers to use user-defined object and location information written in a [TOML] file.

## Requirements

- **Python:** 3.6, 3.7, or 3.8 (tested by author)
- **Dependencies:** See [pyproject.toml](https://github.com/astropenguin/azely/blob/master/pyproject.toml)

## Installation

```shell
$ pip install azely
```

## Basic usage

```python
>>> import azely
```

### Compute function

```python
>>> df = azely.compute(object, site, time, view, ...)
```

This means that `azely` will `compute` az/el of `object` observed from `site` at (on) `time` in `view`.
For example, the following code means that Azely will compute az/el of Sun observed from ALMA AOS on Jan. 1st 2020 in UTC.

```python
>>> df = azely.compute('Sun', 'ALMA AOS', '2020-01-01', 'UTC')
```

| Parameter | Acceptable format | Description | Examples |
| --- | --- | --- | --- |
| `object` | `<obj. name>` | query for object to be searched | `'Sun'`, `'NGC1068'` |
| | `<toml>:<obj. name>` | user-defined object to be loaded (see below) | `'user.toml:M42'`, `'user:M42'` (also valid) |
| `site` | `'here'` (default) | current location (guess by IP address) | - |
| | `<loc. name>` | query for location to be searched | `'ALMA AOS'`, `'Tokyo'` |
| | `<toml>:<loc. name>` | user-defined location to be loaded (see below) | `'user.toml:ASTE'`, `'user:ASTE'` (also valid) |
| `time` | `'now'` (default) | current time | - |
| | `'today'` | one-day time range today | - |
| | `<time>` | start time of one-day time range | `'2020-01-01'`, `'1/1 12:00'`, `'Jan. 1st'` |
| | `<time> to <time>` | start and end of time range | `'1/1 to 1/3'`, `'Jan. 1st to Jan. 3rd'` |
| `view` | `''` (default) | timezone of `site` is used | - |
| | `<tz name>` | name of timezone database | `'Asia/Tokyo'`, `'UTC'` |
| | `<loc. name>` | query for location from which timezone is identified | same as above |
| | `<toml>:<loc. name>` | user-defined location from which timezone is identified | same as above |

### Output DataFrame

```python
>>> df = azely.compute('Sun', 'ALMA AOS', '2020-01-01')
>>> print(df)
```
```
                                   az         el             lst
America/Santiago
2020-01-01 00:00:00-03:00  208.032099 -38.557365 05:09:57.683037
2020-01-01 00:10:00-03:00  205.386419 -39.591843 05:19:59.325780
2020-01-01 00:20:00-03:00  202.642248 -40.528580 05:30:00.968522
2020-01-01 00:30:00-03:00  199.804512 -41.361909 05:40:02.611264
2020-01-01 00:40:00-03:00  196.880119 -42.086416 05:50:04.254007
...                               ...        ...             ...
2020-01-01 23:20:00-03:00  217.754580 -33.555103 04:33:47.666959
2020-01-01 23:30:00-03:00  215.521080 -34.928337 04:43:49.309701
2020-01-01 23:40:00-03:00  213.185460 -36.226931 04:53:50.952444
2020-01-01 23:50:00-03:00  210.746470 -37.445323 05:03:52.595186
2020-01-02 00:00:00-03:00  208.204042 -38.577785 05:13:54.237928

[145 rows x 3 columns]
```

### Examples

## Advanced usage

### Plotting in local sidereal time

### User-defined information

### Cached information

### Customization

## References

- [astropy]
- [matplotlib]
- [pandas]
- [TOML]

<!-- references -->
[astropy]: https://astropy.org
[matplotlib]: https://matplotlib.org
[pandas]: https://pandas.pydata.org
[TOML]: https://github.com/toml-lang/toml
