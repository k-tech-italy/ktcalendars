import datetime
import typing
from contextlib import nullcontext as does_not_raise

import pytest

from ktcalendars import dt


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
            pytest.raises(ValueError, match="day is out of range for month"),
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
