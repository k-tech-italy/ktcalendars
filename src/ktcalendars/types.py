"""Specialised ktcalendars data types."""

from __future__ import annotations

import datetime
import typing

from ktcalendars.days import KTDay


KTDayType: typing.TypeAlias = KTDay | datetime.date | str
