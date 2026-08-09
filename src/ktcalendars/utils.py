from __future__ import annotations

import datetime
import os

import holidays


def dt(dat: str) -> datetime.date | None:
    """Parse a date string into a datetime.date or None."""
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
    """Generate the appropriate country holidays."""
    hol_calendar = country_calendar_code or os.environ.get("DEFAULT_HOLIDAYS_CALENDAR") or "GB-ENG"
    subdiv = None
    if "-" in hol_calendar:
        country, subdiv = hol_calendar.split("-")
    else:
        country = hol_calendar
    cal = holidays.country_holidays(country, subdiv)
    cal.weekend = {6}  # SUN
    return cal
