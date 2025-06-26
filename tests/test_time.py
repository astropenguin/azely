# dependencies
import azely
import pandas as pd


# test functions
def test_get_time() -> None:
    expected = azely.Time("00:00 today", "00:00 tomorrow", "10min", "")

    assert azely.get_time("") == expected
    assert azely.get_time(";;;") == expected
    assert azely.get_time("00:00 today") == expected
    assert azely.get_time(";00:00 tomorrow") == expected
    assert azely.get_time(";;10min") == expected
    assert azely.get_time("00:00 today;00:00 tomorrow") == expected
    assert azely.get_time("00:00 today;;10min") == expected
    assert azely.get_time("00:00 today;00:00 tomorrow;10min") == expected


def test_time_to_index() -> None:
    expected = pd.date_range(
        "2020-01-01",
        "2020-01-07",
        None,
        freq="10min",
        tz="Asia/Tokyo",
        inclusive="left",
    )

    def assert_(time: azely.Time, expected: pd.DatetimeIndex):
        assert (time.index == expected).all()

    def assert_not(time: azely.Time, expected: pd.DatetimeIndex):
        assert not (time.index == expected).all()

    assert_(azely.Time("2020-01-01 JST", "2020-01-07", "10min", ""), expected)
    assert_(azely.Time("2020-01-01", "2020-01-07 JST", "10min", ""), expected)
    assert_(azely.Time("2020-01-01 JST", "2020-01-07 JST", "10min", ""), expected)
    assert_(azely.Time("2020-01-01 JST", "2020-01-07", "10min", "UTC"), expected)
    assert_(azely.Time("2020-01-01", "2020-01-07 JST", "10min", "UTC"), expected)
    assert_(azely.Time("2020-01-01 JST", "2020-01-07 JST", "10min", "UTC"), expected)
    assert_(azely.Time("2020-01-01", "2020-01-07", "10min", "Asia/Tokyo"), expected)
    assert_not(azely.Time("2020-01-01", "2020-01-07", "10min", "UTC"), expected)
