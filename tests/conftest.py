import pytest

from ktcalendars.config import reset_configuration


@pytest.fixture(autouse=True)
def _reset_configuration():
    """Reload the configuration singleton around each test."""
    reset_configuration()
    yield
    reset_configuration()
