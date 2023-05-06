# standard library
from dataclasses import asdict
from tempfile import NamedTemporaryFile


# dependencies
from azely.location import Location, get_location
from tomlkit import dump


# constants
expected = Location(
    name="Array Operations Site",
    longitude="292d14m45.85512974s",
    latitude="-23d01m23.0367s",
    altitude="0.0 m",
)


# test functions
def test_location_by_query():
    assert get_location(f"{expected.name}!") == expected


def test_location_by_user():
    with NamedTemporaryFile("w", suffix=".toml") as f:
        name = "AOS"
        query = f"{f.name}:{name}"

        dump({name: asdict(expected)}, f)
        f.seek(0)

        assert get_location(query) == expected
