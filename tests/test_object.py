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
        longitude="12h29m06.69982572s",
        latitude="2d03m08.59762998s",
        frame="icrs",
    ),
    Object(
        name="3C 345",
        longitude="16h42m58.80997043s",
        latitude="39d48m36.9939552s",
        frame="icrs",
    ),
]


# test functions
@mark.parametrize("obj", objects)
def test_get_object(obj: Object) -> None:
    with NamedTemporaryFile("w", suffix=".toml") as f:
        dump({obj.name: asdict(obj)}, f)

        # save an object to the TOML file
        assert get_object(obj.name, source=f.name) == obj
        # read the object from the TOML file
        assert get_object(obj.name, source=f.name) == obj
