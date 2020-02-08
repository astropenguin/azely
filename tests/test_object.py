# dependent packages
import azely


# constants
expected_solar = azely.object.Object(
    name="Sun", frame="solar", longitude="NaN", latitude="NaN"
)

expected_query = azely.object.Object(
    name="NGC1068", frame="icrs", longitude="02h42m40.771s", latitude="-00d00m47.84s",
)


# test functions
def test_object_of_solar():
    assert azely.get_object(expected_solar.name) == expected_solar


def test_object_by_query():
    assert azely.get_object(expected_query.name) == expected_query
