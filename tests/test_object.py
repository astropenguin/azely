# standard library
from dataclasses import asdict
from tempfile import NamedTemporaryFile


# dependencies
from azely.object import Object, get_object
from pytest import mark
from tomlkit import dump


# test data
objects = [
    Object(
        name="Sun",
        longitude="NA",
        latitude="NA",
        frame="solar",
    ),
    Object(
        name="3C 273",
        longitude="187d16m40.49738576s",
        latitude="2d03m08.59762998s",
        frame="icrs",
    ),
    Object(
        name="3C 345",
        longitude="250d44m42.14955645s",
        latitude="39d48m36.9939552s",
        frame="icrs",
    ),
]


# test functions
@mark.parametrize("expected", objects)
def test_get_object(expected: Object) -> None:
    with NamedTemporaryFile("w", suffix=".toml") as f:
        dump({expected.name: asdict(expected)}, f)

        # save an object to the TOML file
        assert get_object(expected.name, source=f.name) == expected

        # read the object from the TOML file
        assert get_object(expected.name, source=f.name) == expected
