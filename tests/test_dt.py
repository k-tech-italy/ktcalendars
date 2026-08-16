import datetime
import typing
from contextlib import nullcontext as does_not_raise

import pytest

from ktcalendars.utils import dt, get_country_holidays


@pytest.mark.parametrize(
    "day, outcome, expectation",
    [
        pytest.param("2021-01-31", datetime.date(2021, 1, 31), does_not_raise(), id="-"),
        pytest.param("2021/01/31", datetime.date(2021, 1, 31), does_not_raise(), id="/"),
        pytest.param("20210131", datetime.date(2021, 1, 31), does_not_raise(), id="8"),
        pytest.param("2021011", None, does_not_raise(), id="short"),
        pytest.param("202101311", None, does_not_raise(), id="long"),
        pytest.param(
            "2021a131",
            None,
            pytest.raises(ValueError, match="time data '2021a131' does not match format '%Y%m%d'"),
            id="bad-chars",
        ),
        pytest.param(
            "20210231",
            None,
            pytest.raises(ValueError, match="range"),
            id="bad-day",
        ),
        pytest.param(
            "20211305",
            None,
            pytest.raises(ValueError, match="unconverted data remains: 5"),
            id="bad-month",
        ),
        pytest.param(
            None,
            None,
            pytest.raises(ValueError, match="Need a string to parse. Got <class 'NoneType'>"),
            id="None",
        ),
    ],
)
def test_dt(day: typing.Any, outcome, expectation):
    with expectation:
        result = dt(day)
        if result is None:
            assert result is outcome
        else:
            assert dt(day) == outcome


def test_get_country_holidays_plain_code():
    cal = get_country_holidays("IT")
    assert datetime.date(2025, 6, 2) in cal  # Festa della Repubblica
    assert cal.weekend == {6}


def test_get_country_holidays_with_subdivision():
    cal = get_country_holidays("GB-ENG")
    assert datetime.date(2025, 8, 25) in cal  # Summer bank holiday (England only)


def test_get_country_holidays_default_code():
    # Without a code, the configuration's default country code (GB-ENG) is used
    cal = get_country_holidays()
    assert datetime.date(2025, 8, 25) in cal
