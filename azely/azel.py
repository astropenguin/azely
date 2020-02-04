__all__ = ["AzEl", "compute_azel", "compute_azels"]


# standard library
from datetime import datetime, timedelta
from itertools import chain
from logging import getLogger

logger = getLogger(__name__)


# dependent packages
import numpy as np
import pandas as pd
from astropy.coordinates import get_body
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.time import Time


# azely modules
import azely
import azely.query as query
import azely.utils as utils


# module constants
CONFIG = azely.config


# Azely's azel class
class AzEl(SkyCoord):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def at(self, datetime=None, timezone=None):
        object_ = self.info.meta["object"]
        location = self.info.meta["location"]

        return compute_azel(object_, location, datetime, timezone)

    @property
    def az(self):
        return self._to_dataframe(SkyCoord(self.altaz).az)

    @property
    def el(self):
        return self._to_dataframe(SkyCoord(self.altaz).alt)

    @property
    def ra(self):
        return self._to_dataframe(SkyCoord(self.icrs).ra)

    @property
    def dec(self):
        return self._to_dataframe(SkyCoord(self.icrs).dec)

    @property
    def l(self):
        return self._to_dataframe(SkyCoord(self.galactic).l)

    @property
    def b(self):
        return self._to_dataframe(SkyCoord(self.galactic).b)

    @property
    def az_lst(self):
        return self._to_dataframe(SkyCoord(self.altaz).az, "lst")

    @property
    def el_lst(self):
        return self._to_dataframe(SkyCoord(self.altaz).alt, "lst")

    @property
    def ra_lst(self):
        return self._to_dataframe(SkyCoord(self.icrs).ra, "lst")

    @property
    def dec_lst(self):
        return self._to_dataframe(SkyCoord(self.icrs).dec, "lst")

    @property
    def l_lst(self):
        return self._to_dataframe(SkyCoord(self.galactic).l, "lst")

    @property
    def b_lst(self):
        return self._to_dataframe(SkyCoord(self.galactic).b, "lst")

    def _to_dataframe(self, angle, index="tz"):
        index = getattr(self, f"_index_{index}")
        data = {self.info.meta["object"]["name"]: angle}
        return pd.DataFrame(data, index)

    @property
    def _index_tz(self):
        if self.info.meta["timezone"] is not None:
            timezone = self.info.meta["timezone"]
        else:
            timezone = self.info.meta["location"]["timezone"]

        name = f"Datetime ({timezone})"
        index = pd.Index(self.obstime.to_datetime(), name=name)
        return index.tz_localize("UTC").tz_convert(timezone)

    @property
    def _index_lst(self):
        utc = self.obstime.utc
        lst = self.obstime.sidereal_time("mean").value
        diff = (np.diff(utc) > 0).astype(int) - (np.diff(lst) > 0).astype(int)
        day = np.insert(diff, 0, 0).cumsum()

        name = "Local Sidereal Time"
        return pd.Index(pd.to_datetime(day + lst / 24, unit="D"), name=name)

    @property
    def _index_utc(self):
        name = "Datetime (UTC)"
        return pd.Index(self.obstime.utc, name=name)

    def __repr__(self):
        object_ = self.info.meta["object"]["name"]
        location = self.info.meta["location"]["name"]

        return f"AzEl({object_} / {location})"


# functions for azel computation
def compute_azel(object_, location=None, datetime=None, timezone=None):
    if isinstance(object_, str):
        object_ = query.get_object(object_)

    if isinstance(location, str) or (location is None):
        location = query.get_location(location)

    if isinstance(datetime, str) or (datetime is None):
        datetime = query.get_datetime(datetime)

    if isinstance(timezone, (str, int, float)):
        timezone = query.get_timezone(timezone)

    # create astropy's time
    obstime = create_obstime(location, datetime, timezone)

    # create astropy's skycoord
    coord = create_skycoord(object_, obstime)

    # update skycoord's information
    coord.info.meta = {"object": object_, "location": location, "timezone": timezone}

    return AzEl(coord)


def compute_azels(objects, location=None, datetime=None, timezone=None):
    location = query.get_location(location)
    datetime = query.get_datetime(datetime)
    timezone = query.get_timezone(timezone)

    all_objects = []

    for obj_or_tag in objects:
        if obj_or_tag.startswith("@"):
            all_objects.append(get_objects(obj_or_tag))
        else:
            all_objects.append([query.get_object(obj_or_tag)])

    for object_ in chain(*all_objects):
        yield compute_azel(object_, location, datetime, timezone)


# subfunctions for azel computation
def create_obstime(location, datetime, timezone):
    if timezone is None:
        timezone = location["timezone"]

    if datetime.tzinfo is None:
        datetime = datetime.tz_localize(timezone).tz_convert("UTC")

    location = EarthLocation(
        lat=location["latitude"],
        lon=location["longitude"],
        height=location.get("altitude", 0),
    )

    return Time(datetime, location=location)


def create_skycoord(object_, obstime):
    object_ = object_.copy()
    name = object_.pop("name")

    try:
        coord = get_body(name, time=obstime)
    except:
        coord = SkyCoord(**object_, obstime=obstime)
    finally:
        coord.location = obstime.location

    return coord


@utils.default_kwargs(**CONFIG["object"])
def get_objects(tag, searchdirs=(".",), **kwargs):
    filename = tag.lstrip("@") + ".toml"

    for searchdir in utils.abspath(*searchdirs):
        path = searchdir / filename

        if path.exists():
            break
    else:
        raise FileNotFoundError(filename)

    kwargs = {"pattern": path.name, "searchdirs": (path.parent,)}

    for object_ in utils.read_toml(path):
        yield query.get_object(object_, **kwargs)
