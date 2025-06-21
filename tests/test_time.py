# dependencies
import pandas as pd
from azely.time import get_time


# constants
expected = pd.date_range(
    "2020-01-01",
    "2020-01-07",
    None,
    freq="10min",
    tz="Asia/Tokyo",
)


# test functions
def test_time_by_tzinfo():
    result = get_time("2020-01-01 to 2020-01-07", "Asia/Tokyo", "10min")
    assert (result == expected).all()


def test_time_by_location():
    result = get_time("2020-01-01 to 2020-01-07", "Tokyo", "10min")
    assert (result == expected).all()
