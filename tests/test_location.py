# standard library
from dataclasses import asdict
from tempfile import NamedTemporaryFile


# dependencies
from azely.location import Location, get_location
from tomlkit import dump


# test data
expected = Location(
    name="Array Operations Site",
    longitude="292d14m45.85512974s",
    latitude="-23d01m23.0367s",
    altitude="0.0 m",
)


# test functions
def test_location_by_query():
    assert get_location(expected.name, update=True) == expected


def test_location_by_user():
    with NamedTemporaryFile("w", suffix=".toml") as f:
        dump({expected.name: asdict(expected)}, f)
        f.seek(0)

        assert get_location(expected.name, source=f.name) == expected
