from __future__ import annotations

import typing

__author__ = "Giovanni Bronzini"
__version__ = "0.9.1"

from ktcalendars.calendar import KTCalendar
from ktcalendars.days import KTDay

try:
    from typing import override
except ImportError:
    override = lambda _func: _func

