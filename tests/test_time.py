# dependent packages
import azely
import pandas as pd


# constants
expected = pd.date_range("2020-01-01", "2020-01-07", None, freq="10T", tz="Asia/Tokyo")


# test functions
def test_time_by_tzinfo():
    result = azely.get_time("2020-01-01 to 2020-01-07", "Asia/Tokyo", "10T")
    assert (result == expected).all()


def test_time_by_location():
    result = azely.get_time("2020-01-01 to 2020-01-07", "Tokyo", "10T")
    assert (result == expected).all()
