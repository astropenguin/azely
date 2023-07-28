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
    longitude="12h30m49.4233848s",
    latitude="+12d23m28.0437s",
    frame="icrs",
)


# test functions
def test_object_of_solar():
    assert get_object(expected_solar.name, update=True) == expected_solar


def test_object_by_query():
    assert get_object(expected_icrs.name, update=True) == expected_icrs


def test_object_by_user():
    with NamedTemporaryFile("w", suffix=".toml") as f:
        dump({expected_icrs.name: asdict(expected_icrs)}, f)
        f.seek(0)

        assert get_object(expected_icrs.name, source=f.name) == expected_icrs
