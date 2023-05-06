# standard library
from dataclasses import asdict
from tempfile import NamedTemporaryFile


# dependencies
from azely.object import Object, get_object
from tomlkit import dump


# constants
expected_solar = Object(
    name="Sun",
    longitude="NA",
    latitude="NA",
    frame="solar",
)

expected_icrs = Object(
    name="M87",
    longitude="12h30m49.42338414s",
    latitude="+12d23m28.0436859s",
    frame="icrs",
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

        dump({name: asdict(expected_icrs)}, f)
        f.seek(0)

        assert get_object(query) == expected_icrs
