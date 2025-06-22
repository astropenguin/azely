# dependencies
import pandas as pd
from azely.time import Time, get_time


# test functions
def test_get_time() -> None:
    expected = Time("00:00 today", "tomorrow", "10min", "")

    assert get_time("") == expected
    assert get_time(";;;") == expected
    assert get_time("00:00 today") == expected
    assert get_time(";tomorrow") == expected
    assert get_time(";;10min") == expected
    assert get_time("00:00 today;tomorrow") == expected
    assert get_time("00:00 today;;10min") == expected
    assert get_time("00:00 today;tomorrow;10min") == expected


def test_time_to_index() -> None:
    expected = pd.date_range(
        "2020-01-01",
        "2020-01-07",
        None,
        freq="10min",
        tz="Asia/Tokyo",
        inclusive="left",
    )

    def assert_(time: Time, expected: pd.DatetimeIndex):
        assert (time.to_index() == expected).all()

    def assert_not(time: Time, expected: pd.DatetimeIndex):
        assert not (time.to_index() == expected).all()

    assert_(Time("2020-01-01 JST", "2020-01-07", "10min", ""), expected)
    assert_(Time("2020-01-01", "2020-01-07 JST", "10min", ""), expected)
    assert_(Time("2020-01-01 JST", "2020-01-07 JST", "10min", ""), expected)
    assert_(Time("2020-01-01 JST", "2020-01-07", "10min", "UTC"), expected)
    assert_(Time("2020-01-01", "2020-01-07 JST", "10min", "UTC"), expected)
    assert_(Time("2020-01-01 JST", "2020-01-07 JST", "10min", "UTC"), expected)
    assert_(Time("2020-01-01", "2020-01-07", "10min", "Asia/Tokyo"), expected)
    assert_not(Time("2020-01-01", "2020-01-07", "10min", "UTC"), expected)
