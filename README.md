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
>>> azely.compute('Sun', 'ALMA AOS', '2020-01-01').el.plot()
```

## Features

- **High-level API:** Azely provides a simple yet powerful `compute()` function. Users can complete most of operation with it (e.g., information acquisition and computation).
- **Handy output:** Azely's output (from `compute()`) is [pandas] DataFrame, a de facto standard data structure of Python. Users can convert it to other formats like CSV and plot it by [matplotlib] using builtin methods.
- **Web information acquisition:** Azely can automatically acquire object and location information (i.e., longitude and latitude) from online services (e.g., catalogues or maps). Obtained information is cached in a local [TOML] file for an offline use.
- **User-defined information:** Azely also offers to use user-defined object and location information written in a [TOML] file.

## Requirements

- Python: 3.6, 3.7, or 3.8

## Installation

```shell
$ pip install azely
```

<!-- references -->
[astropy]: https://astropy.org
[matplotlib]: https://matplotlib.org
