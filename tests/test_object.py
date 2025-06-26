# standard library
from dataclasses import asdict
from tempfile import NamedTemporaryFile


# dependencies
import azely
from astropy.coordinates import Angle
from astropy.time import Time
from pytest import mark
from tomlkit import dump


# test data
objects = [
    azely.Object(
        name="Sun",
        longitude="NA",
        latitude="NA",
        frame="solar",
    ),
    azely.Object(
        name="3C 273",
        longitude="187d16m40.497384s",
        latitude="2d03m08.597628s",
        frame="icrs",
    ),
    azely.Object(
        name="3C 345",
        longitude="250d44m42.149544s",
        latitude="39d48m36.99396s",
        frame="icrs",
    ),
]


# test functions
@mark.parametrize("expected", objects)
def test_get_object(expected: azely.Object) -> None:
    with NamedTemporaryFile("w", suffix=".toml") as f:
        dump({expected.name: asdict(expected)}, f)
        now = Time.now()

        # save an object to the TOML file
        left = azely.get_object(expected.name, source=f.name).skycoord(now)
        right = expected.skycoord(now)
        assert left.separation(right) < Angle(1, "mas")

        # read the object from the TOML file
        left = azely.get_object(expected.name, source=f.name).skycoord(now)
        right = expected.skycoord(now)
        assert left.separation(right) < Angle(1, "mas")
