"""KTDay module."""

from __future__ import annotations

import datetime
import typing

from dateutil.relativedelta import relativedelta

from ktcalendars.config import get_configuration
from ktcalendars.utils import dt


if typing.TYPE_CHECKING:
    from collections.abc import Iterator

    from ktcalendars.calendar import KTCalendar


__all__ = ["KTDay"]


class KTDay:
    """Utility class for a day."""

    non_working_days = ["Sat", "Sun"]

    def __init__(
        self, day: KTDay | datetime.date | str | None = None, ktcalendar: KTCalendar | None = None, **kwargs: object
    ) -> None:
        """Initialize a KTDay.

        `day` can be another KTDay, a datetime.date, a date string parseable
        by `ktcalendars.utils.dt` or None (today). If a `ktcalendar` is
        provided, its country calendar code is used for holiday checks;
        any extra keyword arguments are set as instance attributes.
        """
        from ktcalendars.calendar import KTCalendar  # noqa: PLC0415

        cal_kwargs: dict[str, typing.Any] = {k[4:]: v for k, v in kwargs.items() if k.startswith("cal_")}
        for k in cal_kwargs:
            del kwargs[f'cal_{k}']

        self.ktcalendar: KTCalendar = ktcalendar or KTCalendar(**cal_kwargs)
        if day is None:
            day = datetime.date.today()
        self.date: datetime.date
        if isinstance(day, KTDay):
            self.date = day.date
        elif isinstance(day, datetime.date):
            self.date = day
        else:
            parsed_date = dt(day)
            if parsed_date is None:
                raise ValueError(f"Invalid date: {day!r}")
            self.date = parsed_date
        self.__dict__.update(kwargs)

    @property
    def day(self) -> int:
        """Return the day number of the day."""
        return self.date.day

    @property
    def month(self) -> int:
        """Return the month number of the day."""
        return self.date.month

    @property
    def year(self) -> int:
        """Return the year of the day."""
        return self.date.year

    @property
    def day_of_year(self) -> int:
        """Return the day of the year."""
        return self.date.timetuple().tm_yday

    @property
    def week_of_year(self) -> int:
        """Return the calendar week of the year for the day."""
        return self.date.isocalendar()[1]

    @property
    def is_extra_holiday(self) -> bool:
        """Return True if this day is in the configuration's holiday overrides."""
        return self.date in get_configuration().get_holiday_overrides(
            self.ktcalendar.country_calendar_code, self.date, self.date
        )

    @property
    def is_holiday(self) -> bool:
        """Return True if this day is a holiday."""
        return self.date in self.ktcalendar.holidays

    @property
    def is_weekend(self) -> bool:
        """Return True if it is a weekend day."""
        return self.date.weekday() in self.ktcalendar.weekend_days

    @property
    def is_workday(self) -> bool:
        """Return true if it is a working day: not a weekend day, nor a holiday, nor an extra holiday."""
        return not (self.is_weekend or self.is_holiday or self.is_extra_holiday)

    @property
    def day_of_week(self) -> str:
        """Return the day of the week."""
        return self.date.strftime("%A")

    @property
    def day_of_week_short(self) -> str:
        """Return the day of the week in short format."""
        return self.date.strftime("%a")

    @property
    def month_name(self) -> str:
        """Return the name of the month."""
        return self.date.strftime("%B")

    @property
    def month_name_short(self) -> str:
        """Return the name of the month in short format."""
        return self.date.strftime("%b")

    def range_to(self, target: datetime.date | KTDay) -> Iterator[KTDay]:
        """Iterate over all days between this day and the target day (both inclusive)."""
        if not isinstance(target, KTDay):
            target = KTDay(target)
        if self.date > target.date:
            raise ValueError("Start date cannot be later than end date.")
        delta_days = (target.date - self.date).days
        for i in range(delta_days + 1):
            yield self + i

    def __eq__(self, __value: object) -> bool:
        """Return True if this day is equal to the given day."""
        if not isinstance(__value, KTDay | datetime.date | str):
            raise NotImplementedError(f"Cannot compare a KTDay with {type(__value)}")
        if not isinstance(__value, KTDay):
            __value = KTDay(__value)
        return self.date == __value.date

    def __hash__(self) -> int:
        return self.date.year * 10000 + self.date.month * 100 + self.date.day

    def __lt__(self, __value: KTDay | datetime.date | str | None) -> bool:
        if not isinstance(__value, KTDay):
            __value = KTDay(__value)
        return hash(self) < hash(__value)

    def __gt__(self, __value: KTDay | datetime.date | str | None) -> bool:
        if not isinstance(__value, KTDay):
            __value = KTDay(__value)
        return hash(self) > hash(__value)

    def __le__(self, __value: KTDay | datetime.date | str | None) -> bool:
        if not isinstance(__value, KTDay):
            __value = KTDay(__value)
        return hash(self) <= hash(__value)

    def __ge__(self, __value: KTDay | datetime.date | str | None) -> bool:
        if not isinstance(__value, KTDay):
            __value = KTDay(__value)
        return hash(self) >= hash(__value)

    def __sub__(self, other: KTDay | int | datetime.date | datetime.timedelta | relativedelta) -> int | KTDay:
        """Subtract a number of days or a time period from this day."""
        if isinstance(other, KTDay):
            return (self.date - other.date).days
        if isinstance(other, int):
            return self.__class__(self.date - relativedelta(days=other), ktcalendar=self.ktcalendar)
        if isinstance(other, datetime.timedelta):
            return self.__class__(self.date - relativedelta(days=other.days), ktcalendar=self.ktcalendar)
        if isinstance(other, relativedelta):
            return self.__class__(
                self.date - relativedelta(years=other.years, months=other.months, days=other.days),
                ktcalendar=self.ktcalendar,
            )
        return self - KTDay(other)

    def __add__(self, other: int | datetime.timedelta | relativedelta) -> KTDay:
        """Add a number of days or a time period to this day.

        If `other` is an `int`, it represents a number of days to add.

        If `other` is a `timedelta`, only days are taken into account,
        without any rounding.

        If `other` is a `relativedelta`, only years, months, days and
        weeks are taken into account. Any relative information with
        finer granularity than days and any absolute information is
        ignored.

        :param other: the number of days or period of time to add.
        :return: a new `KTDay` instance.
        """
        if isinstance(other, int):
            delta = relativedelta(days=other)
        elif isinstance(other, datetime.timedelta):
            delta = relativedelta(days=other.days)
        elif isinstance(other, relativedelta):
            delta = relativedelta(years=other.years, months=other.months, days=other.days)
        else:
            raise TypeError(f"Cannot add {type(other)} to a KTDay")
        return KTDay(self.date + delta)

    def __repr__(self) -> str:
        return self.date.strftime("K%Y-%m-%d")

    def __str__(self) -> str:
        return self.date.strftime("%Y-%m-%d")
