# standard library
from tempfile import NamedTemporaryFile


# dependent packages
from azely.location import Location, get_location
from toml import dump


# constants
expected = Location(
    name="Array Operations Site",
    longitude="-67.75392913062831",
    latitude="-23.02306575",
    altitude="0",
)


# test functions
def test_location_by_query():
    assert get_location(expected.name) == expected


def test_location_by_user():
    with NamedTemporaryFile("w", suffix=".toml") as f:
        name = "AOS"
        query = f"{f.name}:{name}"

        dump({name: expected.to_dict()}, f)
        f.seek(0)

        assert get_location(query) == expected
