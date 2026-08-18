"""Module for Date Ranges."""

from __future__ import annotations

import datetime
import typing

from dateutil import relativedelta
from psycopg.types.range import DateRange, Range

from ktcalendars.calendar import KTCalendar
from ktcalendars.days import KTDay


if typing.TYPE_CHECKING:
    from collections.abc import Iterable, Iterator

    from ktcalendars.types import KTDayType


def _lo(period: Range[datetime.date]) -> datetime.date:
    """Return the lower bound, with an infinite bound replaced by datetime.date.min."""
    return period.lower or datetime.date.min


def _hi(period: Range[datetime.date]) -> datetime.date:
    """Return the upper bound, with an infinite bound replaced by datetime.date.max."""
    return period.upper or datetime.date.max


class KTDateRange(DateRange):
    """A specialised version of DateRange.

    It also accepts:
      - a DateRange
      - KTDay | str as lower&upper boundaries

    Ranges are always stored in the PostgreSQL canonical form for discrete types: the lower bound is
    included and the upper bound is excluded, that is [). Bounds given with a different inclusivity
    are shifted accordingly (dates are discrete), and a range that canonicalises to nothing (e.g.
    equal bounds with [) inclusivity) becomes the empty range, exactly as PostgreSQL does.

    In the comparison methods, `other` can be a range or a single day; a single day is treated as
    the one-day range covering it.

    Like KTDay, a range is bound to a KTCalendar: pass one with `ktcalendar`, or let the range
    create its own — `cal_`-prefixed keyword arguments are forwarded to the KTCalendar constructor,
    and without them a KTDateRange passed as `lower` hands down its own calendar. The calendar binds
    every KTDay the range produces; any remaining keyword arguments are set as instance attributes.
    """

    def __init__(
        self,
        lower: Range[datetime.date]
        | KTDayType
        | tuple[KTDayType | None, KTDayType | None]
        | list[KTDayType | None]
        | None = None,
        upper: KTDayType | None = None,
        bounds: str = '[)',
        empty: bool = False,
        ktcalendar: KTCalendar | None = None,
        **kwargs: object,
    ) -> None:
        cal_kwargs: dict[str, typing.Any] = {k[4:]: v for k, v in kwargs.items() if k.startswith('cal_')}
        for k in cal_kwargs:
            del kwargs[f'cal_{k}']

        self.ktcalendar: KTCalendar
        if ktcalendar is not None:
            self.ktcalendar = ktcalendar
        elif not cal_kwargs and isinstance(lower, KTDateRange):
            self.ktcalendar = lower.ktcalendar
        else:
            self.ktcalendar = KTCalendar(**cal_kwargs)

        start: datetime.date | None
        end: datetime.date | None
        if isinstance(lower, Range):
            start, end, bounds, empty = lower.lower, lower.upper, lower.bounds, lower.isempty
        else:
            if isinstance(lower, tuple | list):
                lower, upper = lower
            if lower is not None:
                start = KTDay(typing.cast('KTDayType', lower), ktcalendar=self.ktcalendar).date
            else:
                start = None
            end = KTDay(upper, ktcalendar=self.ktcalendar).date if upper is not None else None
        if start is not None and end is not None and start > end:
            raise ValueError('Lower bound must be smaller than upper bound')
        if not empty:
            if bounds not in ('[)', '(]', '()', '[]'):
                raise ValueError(f'bound flags not valid: {bounds!r}')
            # Canonicalise to [) like PostgreSQL: dates are discrete, so shifting by one day
            # preserves the covered days while normalising the bound inclusivity.
            if start is not None and bounds[0] == '(':
                start += datetime.timedelta(days=1)
            if end is not None and bounds[1] == ']':
                end += datetime.timedelta(days=1)
            bounds = '[)'
            if start is not None and end is not None and start >= end:
                start = end = None
                empty = True
        super().__init__(start, end, bounds, empty)
        self.__dict__.update(kwargs)

    @staticmethod
    def from_start_end(
        start_date: KTDayType, end_date: KTDayType, ktcalendar: KTCalendar | None = None, **kwargs: object
    ) -> KTDateRange:
        """Build a KTDateRange from a start and end date (included)."""
        extra: dict[str, typing.Any] = dict(kwargs)
        return KTDateRange(lower=start_date, upper=end_date, bounds='[]', ktcalendar=ktcalendar, **extra)

    @staticmethod
    def gaps(
        ranges: Iterable[Range[datetime.date] | KTDayType],
        start_date: KTDayType,
        end_date: KTDayType,
        ktcalendar: KTCalendar | None = None,
    ) -> list[KTDateRange]:
        """Return the sub-ranges of [start_date, end_date] (both included) not covered by `ranges`.

        `ranges` must be non-overlapping; a single day is treated as the one-day range covering it.
        Gaps are returned as canonical [) ranges, sorted ascending, bound to the given (or a new)
        KTCalendar.
        """
        window = KTDateRange.from_start_end(start_date, end_date, ktcalendar=ktcalendar)
        cursor = typing.cast('datetime.date', window.lower)
        result: list[KTDateRange] = []
        for r in sorted((r for r in map(window._as_range, ranges) if r.overlap(window)), key=_lo):
            if _lo(r) > cursor:
                result.append(KTDateRange(cursor, _lo(r), ktcalendar=window.ktcalendar))
            cursor = max(cursor, _hi(r))
            if cursor >= typing.cast('datetime.date', window.upper):
                return result
        result.append(KTDateRange(cursor, window.upper, ktcalendar=window.ktcalendar))
        return result

    def _as_range(
        self,
        other: Range[datetime.date] | KTDayType | tuple[KTDayType | None, KTDayType | None] | list[KTDayType | None],
    ) -> KTDateRange:
        """Coerce `other` to a KTDateRange bound to this range's calendar.

        A single day becomes the one-day range covering it.
        """
        if isinstance(other, KTDateRange):
            return other
        if isinstance(other, Range | tuple | list):
            return KTDateRange(other, ktcalendar=self.ktcalendar)
        return KTDateRange.from_start_end(other, other, ktcalendar=self.ktcalendar)

    def fully_lt(self, other: Range[datetime.date] | KTDayType) -> bool:
        """Return True if the given date range is fully before the other."""
        other = self._as_range(other)
        if self.isempty or other.isempty:
            return False
        return _hi(self) <= _lo(other)

    def fully_gt(self, other: Range[datetime.date] | KTDayType) -> bool:
        """Return True if the given date range is fully after the other."""
        other = self._as_range(other)
        if self.isempty or other.isempty:
            return False
        return _lo(self) >= _hi(other)

    def startsbefore(self, other: Range[datetime.date] | KTDayType) -> bool:
        """Return True if the given date range start date is before the other's."""
        other = self._as_range(other)
        if self.isempty or other.isempty:
            return False
        return _lo(self) < _lo(other)

    def startsafter(self, other: Range[datetime.date] | KTDayType) -> bool:
        """Return True if the given date range start date is after the other's."""
        other = self._as_range(other)
        if self.isempty or other.isempty:
            return False
        return _lo(self) > _lo(other)

    def endsbefore(self, other: Range[datetime.date] | KTDayType) -> bool:
        """Return True if the given date range end date is before the other's."""
        other = self._as_range(other)
        if self.isempty or other.isempty:
            return False
        return _hi(self) < _hi(other)

    def endsafter(self, other: Range[datetime.date] | KTDayType) -> bool:
        """Return True if the given date range end date is after the other's."""
        other = self._as_range(other)
        if self.isempty or other.isempty:
            return False
        return _hi(self) > _hi(other)

    def precedes(self, other: Range[datetime.date] | KTDayType) -> bool:
        """Return True if the given date range is adjacent and precedes the other."""
        other = self._as_range(other)
        if self.isempty or other.isempty:
            return False
        return _hi(self) == _lo(other)

    def follows(self, other: Range[datetime.date] | KTDayType) -> bool:
        """Return True if the given date range is adjacent and follows the other."""
        other = self._as_range(other)
        if self.isempty or other.isempty:
            return False
        return _lo(self) == _hi(other)

    def as_dates(self) -> tuple[datetime.date | None, datetime.date | None]:
        """Return the object as a PG DateRange replacing infinite boundaries with datetime.date.min/max."""
        if self.isempty:
            raise ValueError('Unable to extract dates: date range is empty')
        lower = (
            datetime.date.min
            if self.lower_inf
            else (self.lower + relativedelta.relativedelta(days=0 if self.lower_inc else 1))
        )
        upper = (
            datetime.date.max
            if self.upper_inf
            else (self.upper - relativedelta.relativedelta(days=0 if self.upper_inc else 1))
        )
        return (lower, upper)

    def contains(self, other: Range[datetime.date] | KTDayType) -> bool:
        """Check if range contains other range (any range contains the empty range)."""
        other = self._as_range(other)
        if other.isempty:
            return True
        if self.isempty:
            return False
        return _lo(self) <= _lo(other) and _hi(self) >= _hi(other)

    def contained_by(self, other: Range[datetime.date] | KTDayType) -> bool:
        """Check if range is contained by other range."""
        return self._as_range(other).contains(self)

    def overlap(self, other: Range[datetime.date] | KTDayType) -> bool:
        """Check if range is overlapping other range (the empty range overlaps nothing)."""
        other = self._as_range(other)
        if self.isempty or other.isempty:
            return False
        return _lo(self) < _hi(other) and _lo(other) < _hi(self)

    def adjacent_to(self, other: Range[datetime.date] | KTDayType) -> bool:
        """Check if range is adjacent to other range (touches at a boundary without overlapping)."""
        return self.precedes(other) or self.follows(other)

    @property
    def boundaries(self) -> tuple[datetime.date | None, datetime.date | None]:
        """Return the range's boundaries."""
        return self.lower, self.upper

    def intersection(self, other: Range[datetime.date] | KTDayType) -> KTDateRange | None:
        """Return the intersection with the other range, or None if they do not overlap."""
        other = self._as_range(other)
        if self.isempty or other.isempty:
            return None
        lower = max(_lo(self), _lo(other))
        upper = min(_hi(self), _hi(other))
        if lower >= upper:
            return None
        return KTDateRange(
            None if lower == datetime.date.min else lower,
            None if upper == datetime.date.max else upper,
            ktcalendar=self.ktcalendar,
        )

    def __contains__(self, x: KTDayType | None) -> bool:
        """Accept dates and KTDay compatible x; None is never in a range."""
        if x is None:
            return False
        return super().__contains__(KTDay(x, ktcalendar=self.ktcalendar).date)

    def __iter__(self) -> Iterator[KTDay]:
        """Return a KTDay iterator over the days in the range.

        The empty range yields nothing; raise TypeError for unbounded ranges.
        """
        if self.isempty:
            return
        lower, upper = self.lower, self.upper
        if lower is None or lower == datetime.date.min or upper is None or upper == datetime.date.max:
            raise TypeError('Cannot iterate over unbounded range')
        day = KTDay(lower, ktcalendar=self.ktcalendar)
        for x in range((upper - lower).days):
            yield day + x

    def __getstate__(self) -> dict[str, typing.Any]:
        """Also persist instance attributes (e.g. the calendar), which the slots-based parent would drop."""
        return {**super().__getstate__(), **self.__dict__}

    def __str__(self) -> str:
        if self.isempty:
            return 'empty'
        res = f'[{self.lower:%Y-%m-%d}:' if self.lower not in [None, datetime.date.min] else '(...:'
        res += f'{self.upper:%Y-%m-%d})' if self.upper not in [None, datetime.date.max] else '...)'
        return res
