"""Specialised ktcalendars data types."""

from __future__ import annotations

import datetime as dt
import typing

from ktcalendars.days import KTDay


KTDayType: typing.TypeAlias = KTDay | dt.date | str
