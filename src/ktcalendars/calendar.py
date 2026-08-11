"""KTCalendar modulee."""

from __future__ import annotations

import datetime
from calendar import Calendar
from typing_extensions import override
from typing import TYPE_CHECKING

from dateutil.relativedelta import relativedelta, MO, SU
from .config import get_configuration
from .days import KTDay

if TYPE_CHECKING:
    from collections.abc import Iterable
    from collections.abc import Iterator


__all__ = ["KTCalendar"]


class KTCalendar(Calendar):
    """A holiday-aware calendar that generates KTDay instances for a country calendar."""

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

        Delegates to the loaded configuration class (see `ktcalendars.config`).
        Override this method to customise.
        """
        return get_configuration().get_default_country_code()

    def get_ktday(self, day: KTDay | datetime.date | str | None = None, **kwargs: object) -> KTDay:
        """Return a calendar-aware KTDay instance."""
        return KTDay(day=day, ktcalendar=self, **kwargs)

    def month_weeks_days(self, year: int, month: int) -> Iterator[KTDay]:
        """Return an iterator for one month.

        The iterator yields KTDay instances and always iterates through
        complete weeks, so it will yield KTDays outside the specified month.
        """
        for x in super().itermonthdates(year, month):
            yield KTDay(x, ktcalendar=self)

    def days_in_months(self, year: int, month: int) -> Iterator[KTDay | None]:
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
    ) -> Iterable[KTDay]:
        """Iterate over all working days between from_date and to_date."""
        for day in self.iter_dates(from_date, to_date):
            if not day.is_non_working_day(country_calendar_code=self.country_calendar_code):
                yield day

    def get_non_work_days(
        self, from_date: KTDay | datetime.date | str, to_date: KTDay | datetime.date | str
    ) -> Iterable[KTDay]:
        """Iterate over all non-working days between from_date and to_date."""
        for day in self.iter_dates(from_date, to_date):
            if day.is_non_working_day(country_calendar_code=self.country_calendar_code):
                yield day

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
