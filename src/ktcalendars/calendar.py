from __future__ import annotations

import datetime
import os
from calendar import Calendar
from typing import override
from collections.abc import Iterator

from dateutil.relativedelta import relativedelta, MO, SU
from .days import KTDay


class KTCalendar(Calendar):
    """A custom calendar class for KRM that generates KrmDays."""

    @override
    def __init__(self, firstweekday: int = 0, country_code: str | None = None) -> None:
        super().__init__(firstweekday)
        if country_code is None:
            self.country_calendar_code = self.__class__.get_default_country_code()
        else:
            self.country_calendar_code = country_code

    @staticmethod
    def get_default_country_code() -> str:
        """Return the default country code.

        Override this method to customise.
        """
        return os.environ.get("DEFAULT_HOLIDAYS_CALENDAR", "GB-ENG")

    def get_ktday(self, day: KTDay | datetime.date | str | None = None, **kwargs: dict) -> KTDay:
        """Return a calendar-aware KTDay instance."""
        from . import KTDay

        return KTDay(day=day, ktcalendar=self, **kwargs)

    def itermonthktdates(self, year: int, month: int) -> Iterator[KTDay | None]:
        """Return an iterator for one month.

        The iterator will yield a KTDay
        values and will always iterate through complete weeks, so it will yield
        KTDates outside the specified month.
        """
        for x in super().itermonthdates(year, month):
            yield KTDay(x, ktcalendar=self)

    def itermonthktdays(self, year: int, month: int) -> Iterator[KTDay | None]:
        """Iterate over the days of the month returning entire weeks.

        If 1st week start mid-week, say for example Wednesday, then the first 2 elements returned will be None.
        (Monday and Tuesday are outside of the month in the example)
        """
        for x in super().itermonthdays(year, month):
            yield KTDay(datetime.date(year, month, x), ktcalendar=self) if x else None

    def iter_dates(
        self, from_date: KTDay | datetime.date | str, to_date: KTDay | datetime.date | str
    ) -> Iterator[KTDay]:
        """Iterate over all dates between from_date and to_date."""
        start = KTDay(from_date)
        end = KTDay(to_date)
        if start > end:
            raise ValueError("Start date cannot be after end date.")
        delta_days = (end.date - start.date).days

        for i in range(delta_days + 1):
            yield KTDay(start.date + datetime.timedelta(days=i), ktcalendar=self)

    def get_work_days(
        self, from_date: KTDay | datetime.date | str, to_date: KTDay | datetime.date | str
    ) -> list[KTDay]:
        """Return the iterator for the work days between from_date and to_date."""
        days_between = self.iter_dates(from_date, to_date)

        return [
            day for day in days_between if not day.is_non_working_day(country_calendar_code=self.country_calendar_code)
        ]

    def week_for(self, date: KTDay | datetime.date | str | None = None) -> tuple[KTDay, KTDay]:
        """Return the start and end date of the week for the given date.

        If no date is given, the current date is used.
        """
        date = KTDay(date).date
        return KTDay(date + relativedelta(weekday=MO(-1)), ktcalendar=self), KTDay(
            date + relativedelta(weekday=SU), ktcalendar=self
        )

    def iter_week(self, date: datetime.date | str | None = None) -> Iterator[KTDay]:
        """Iterate over all dates in the week for the given date.

        If no date is given, the current date is used.
        """
        return self.iter_dates(*self.week_for(date))
