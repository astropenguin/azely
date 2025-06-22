# standard library
from dataclasses import asdict
from tempfile import NamedTemporaryFile


# dependencies
from azely.location import Location, get_location
from pytest import mark
from tomlkit import dump


# test data
locations = [
    Location(
        name="Atacama Large Millimeter/submillimeter Array",
        longitude="-67d45m11.06028s",
        latitude="-23d01m21.97704s",
        altitude="0.0 m",
    ),
    Location(
        name="Nobeyama Radio Astronomy Observatory",
        longitude="138d28m25.28616s",
        latitude="35d56m34.76364s",
        altitude="0.0 m",
    ),
]


# test functions
@mark.parametrize("expected", locations)
def test_get_location(expected: Location, /) -> None:
    with NamedTemporaryFile("w", suffix=".toml") as f:
        dump({expected.name: asdict(expected)}, f)

        # save an object to the TOML file
        location = get_location(expected.name, source=f.name)
        assert location.longitude == expected.longitude
        assert location.latitude == expected.latitude

        # read the object from the TOML file
        location = get_location(expected.name, source=f.name)
        assert location.longitude == expected.longitude
        assert location.latitude == expected.latitude
