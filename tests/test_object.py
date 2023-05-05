# standard library
from tempfile import NamedTemporaryFile


# dependencies
from azely.object import Object, get_object
from tomlkit import dump


# constants
expected_solar = Object(
    name="Sun",
    frame="solar",
    longitude="",
    latitude="",
)

expected_icrs = Object(
    name="NGC1068",
    frame="icrs",
    longitude="02h42m40.7091672s",
    latitude="-00d00m47.859696s",
)


# test functions
def test_object_of_solar():
    assert get_object(f"{expected_solar.name}!") == expected_solar


def test_object_by_query():
    assert get_object(f"{expected_icrs.name}!") == expected_icrs


def test_location_by_user():
    with NamedTemporaryFile("w", suffix=".toml") as f:
        name = "AOS"
        query = f"{f.name}:{name}"

        dump({name: expected_icrs.to_dict()}, f)
        f.seek(0)

        assert get_object(query) == expected_icrs
