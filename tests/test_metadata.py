# dependencies
import azely


# test functions
def test_version():
    """Make sure the version is valid."""
    assert azely.__version__ == "0.7.0"
