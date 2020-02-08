# dependent packages
import azely


# constants
expected = azely.location.Location(
    name="Array Operations Site",
    longitude="-67.75392913062831",
    latitude="-23.02306575",
    altitude="0",
)


# test functions
def test_location():
    assert azely.get_location(expected.name) == expected
