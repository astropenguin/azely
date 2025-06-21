__all__ = ["AzEl", "compute"]


# dependent packages
from pandas import DataFrame, DatetimeIndex, Timestamp, to_timedelta
from .location import Location, get_location
from .object import Object, get_object
from .time import Time, get_time


# constants
from .consts import (
    DAYFIRST,
    FRAME,
    FREQ,
    SITE,
    TIME,
    TIMEOUT,
    VIEW,
    YEARFIRST,
)

SOLAR_TO_SIDEREAL = 1.002_737_909


# data class
class AzEl(DataFrame):
    """Subclass of pandas DataFrame with special properties for Azely."""

    #: allowed custom attributes
    _metadata = ["object", "site"]

    @property
    def alt(self):
        """Alias of ``dataframe.el``."""
        return self.el

    @property
    def in_lst(self):
        """Convert time index to LST."""
        td = self.index - self.index[0]
        td_lst = td * SOLAR_TO_SIDEREAL + self.lst[0]
        td_lst = td_lst.floor("1D") + self.lst

        lst = Timestamp(0) + td_lst
        return self.set_index(DatetimeIndex(lst, name="LST"))

    @property
    def in_utc(self):
        """Convert time index to UTC."""
        utc = self.index.tz_convert("UTC")  # type: ignore
        return self.set_index(DatetimeIndex(utc, name="UTC"))

    @property
    def _constructor(self):
        """Constructor of class."""
        return AzEl


# main functions
def compute(
    object: str,
    site: str = SITE,
    time: str = TIME,
    view: str | None = VIEW,
    frame: str = FRAME,
    freq: str = FREQ,
    dayfirst: bool = DAYFIRST,
    yearfirst: bool = YEARFIRST,
    timeout: float = TIMEOUT,
) -> AzEl:
    """Compute az/el and local sidereal time (LST) of an astronomical object.

    The ``compute`` function (1) gets object, location, and time information, (2) computes
    az/el and LST (local sidereal time), and (3) returns them as a pandas DataFrame.

    Object information can be obtained either online (CDS) or offline (an user-defined
    TOML file) by query (e.g., ``'NGC1068'`` or ``'Sun'``). Location information can be
    obtained either online (IP address or OpenStreetMap) or offline (an user-defined
    TOML file) by query (e.g., ``'Tokyo'`` or ``'ALMA AOS'``). Time information can be
    computed from either formatted (e.g., ``'2020-01-01'``) and natural language-like
    query (e.g., ``'Jan 1st 2020'``). See docstrings of ``get_[object|location|time]``
    functions for more detailed query options.

    There are two different locations to be used for a computation:
    (1) ``site``: location where az/el of an object is computed.
    (2) ``view``: location where time information (timezone) is considered.

    Args:
        object: Query string for object information (e.g., ``'Sun'`` or ``'NGC1068'``).
            Specify ``'user:NGC1068'`` if users want to get information from ``user.toml``.
        site: Query string for location information at a site (e.g., ``'Tokyo'``).
            Specify ``'user:Tokyo'`` if users want to get information from ``user.toml``.
        time: Query string for time information at a view (e.g., ``'2020-01-01'``).
        view: Query string for timezone information at the view. (e.g., ``'Asia/Tokyo'``,
            ``'UTC'``, or ``Tokyo``). By default (``''``),  timezone at the site is used.
        frame: (object option) Name of equatorial coordinates used in astropy's SkyCoord.
        freq: (time option) Frequency of time samples as the same format of pandas offset
            aliases (e.g., ``'1D'`` -> 1 day, ``'3h'`` -> 3 hours, ``'10min'`` -> 10 minutes).
        dayfirst: (time option) Whether to interpret the first value in an ambiguous
            3-integer date (e.g., ``'01-02-03'``) as the day. If True, for example,
            ``'01-02-03'`` is treated as Feb. 1st 2003.
        yearfirst: (time option) Whether to interpret the first value in an ambiguous
            3-integer date (e.g., ``'01-02-03'``) as the year. If True, for example,
            ``'01-02-03'`` is treated as Feb. 3rd 2001. If ``dayfirst`` is also ``True``,
            then it will be Mar. 2nd 2001.
        timeout: (common option) Query timeout expressed in units of seconds.

    Returns:
        Computed DataFrame of object's az/el and LST at given site and view.

    Raises:
        AzelyError: Raised if one of mid-level APIs fails to get any information.

    Examples:
        To compute daily az/el of NGC1068 at ALMA AOS::

            >>> df = azely.compute('NGC1068', 'ALMA AOS', '2020-02-01')

        To compute the same object and location but view from Japan::

            >>> df = azely.compute('NGC1068', 'ALMA AOS', '2020-02-01', view='Tokyo')

        To compute az/el of Sun at noon during an year at Tokyo::

            >>> df = azely.compute('Sun', 'Tokyo', '1/1 12:00 to 12/31 12:00', freq='1D')

    """  # noqa: E501
    object_ = get_object(object, frame=frame, timeout=timeout)
    site_ = get_location(site, timeout=timeout)
    time_ = get_time(time, view or site, freq, dayfirst, yearfirst, timeout)

    return _compute(object_, site_, time_)


# helper functions
def _compute(object: Object, site: Location, time: Time) -> AzEl:
    """Compute az/el and local sidereal time (LST) of an astronomical object.

    Similar to ``compute`` function, but this function receives instances
    of ``Object``, ``Location``, and ``Time`` classes as arguments.

    Args:
        object: Object information.
        site: Site location information.
        time: Time information.

    Returns:
        Computed DataFrame of object's az/el and LST at given site and view.

    Raises:
        AzelyError: Raised if one of mid-level APIs fails to get any information.

    """
    obstime = time.to_obstime(site.to_earthlocation())
    skycoord = object.to_skycoord(obstime)

    az = skycoord.altaz.az  # type: ignore
    el = skycoord.altaz.alt  # type: ignore
    lst = to_timedelta(obstime.sidereal_time("mean").value, unit="hr")

    azel = AzEl(dict(az=az, el=el, lst=lst), index=time.to_index())
    azel.object = object
    azel.site = site
    return azel
