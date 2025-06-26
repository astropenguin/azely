# standard library
from dataclasses import asdict
from tempfile import NamedTemporaryFile


# dependencies
import azely
from astropy.coordinates import Distance
from pytest import mark
from tomlkit import dump


# test data
locations = [
    azely.Location(
        name="Atacama Large Millimeter/submillimeter Array",
        longitude="-67d45m11.06028s",
        latitude="-23d01m21.97704s",
        altitude="-3.8089945457383293e-10 m",
    ),
    azely.Location(
        name="Nobeyama Radio Astronomy Observatory",
        longitude="138d28m25.28616s",
        latitude="35d56m34.76364s",
        altitude="2.1695119188480857e-11 m",
    ),
]


# test functions
@mark.parametrize("expected", locations)
def test_get_location(expected: azely.Location) -> None:
    with NamedTemporaryFile("w", suffix=".toml") as f:
        dump({expected.name: asdict(expected)}, f)

        # save an object to the TOML file
        left = azely.get_location(expected.name, source=f.name).earthlocation.itrs
        right = expected.earthlocation.itrs
        assert left.separation_3d(right) < Distance(1, "m")

        # read the object from the TOML file
        left = azely.get_location(expected.name, source=f.name).earthlocation.itrs
        right = expected.earthlocation.itrs
        assert left.separation_3d(right) < Distance(1, "m")
