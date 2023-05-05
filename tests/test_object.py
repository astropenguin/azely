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
    name="M87",
    frame="icrs",
    longitude="12h30m49.42338414s",
    latitude="+12d23m28.0436859s",
)


# test functions
def test_object_of_solar():
    assert get_object(f"{expected_solar.name}!") == expected_solar


def test_object_by_query():
    assert get_object(f"{expected_icrs.name}!") == expected_icrs


def test_object_by_user():
    with NamedTemporaryFile("w", suffix=".toml") as f:
        name = "M87"
        query = f"{f.name}:{name}"

        dump({name: expected_icrs.to_dict()}, f)
        f.seek(0)

        assert get_object(query) == expected_icrs
