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
        altitude="-3.8089945457383293e-10 m",
    ),
    Location(
        name="Nobeyama Radio Astronomy Observatory",
        longitude="138d28m25.28616s",
        latitude="35d56m34.76364s",
        altitude="2.1695119188480857e-11 m",
    ),
]


# test functions
@mark.parametrize("obj", locations)
def test_get_location(obj: Location) -> None:
    with NamedTemporaryFile("w", suffix=".toml") as f:
        dump({obj.name: asdict(obj)}, f)

        # save an object to the TOML file
        assert get_location(obj.name, source=f.name) == obj
        # read the object from the TOML file
        assert get_location(obj.name, source=f.name) == obj
