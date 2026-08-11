"""Utility helpers for date parsing and country holiday calendar lookup."""

from __future__ import annotations

import datetime

import holidays

from ktcalendars.config import get_configuration


def dt(dat: str) -> datetime.date | None:
    """Parse a date string into a datetime.date.

    Accepted formats are ``YYYY-MM-DD``, ``YYYY/MM/DD`` and ``YYYYMMDD``.
    Returns None if the string has an unexpected length; raises ValueError
    if the argument is not a string or does not match any accepted format.
    """
    if not isinstance(dat, str):
        raise ValueError(f"Need a string to parse. Got {type(dat)}")
    if len(dat) not in (8, 10):
        return None
    if "-" in dat:
        return datetime.datetime.strptime(dat, "%Y-%m-%d").date()
    if "/" in dat:
        return datetime.datetime.strptime(dat, "%Y/%m/%d").date()
    return datetime.datetime.strptime(dat, "%Y%m%d").date()


def get_country_holidays(country_calendar_code: str | None = None) -> holidays.HolidayBase:
    """Return the holiday calendar for the given country calendar code.

    The code is either a country code (e.g. ``"IT"``) or a country code with
    a subdivision (e.g. ``"GB-ENG"``). When None, the default country code
    of the loaded configuration class (see `ktcalendars.config`) is used.
    """
    hol_calendar = country_calendar_code or get_configuration().get_default_country_code()
    subdiv = None
    if "-" in hol_calendar:
        country, subdiv = hol_calendar.split("-")
    else:
        country = hol_calendar
    cal = holidays.country_holidays(country, subdiv)
    cal.weekend = {6}  # SUN
    return cal
