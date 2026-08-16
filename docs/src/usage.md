---
title: Getting started
---

# How to use ktcalendars

## Configuration

### The configuration class

ktcalendars is configured through a single pluggable *configuration class*.
By default the built-in `DefaultConfiguration` is used; to customise the
behaviour, subclass `AbstractConfiguration` and set the `KTCALENDAR_CONFIG`
environment variable to the fully qualified name of your subclass:

```shell
export KTCALENDAR_CONFIG=mypackage.config.CompanyConfiguration
```

The configuration is loaded lazily on first use and cached; tests can call
`ktcalendars.config.reset_configuration()` to reload it after changing
environment variables.

### Country calendar codes

Holiday lookups are driven by a *country calendar code*: either a plain
ISO country code (e.g. `IT`) or a country code plus subdivision separated
by a dash (e.g. `GB-ENG`, `US-CA`). Any code supported by the
[holidays](https://pypi.org/project/holidays/) package works.

The default code is resolved in this order:

1. the `country_code` passed to `KTCalendar(...)`;
2. the configuration class's `get_default_country_code()`, which by default
   resolves:
    1. the `KTCALENDAR_COUNTRY` environment variable;
    2. the `DEFAULT_HOLIDAYS_CALENDAR` environment variable (**deprecated**,
       use `KTCALENDAR_COUNTRY` instead);
    3. `GB-ENG`.

You can also change the default for your whole application by subclassing
`KTCalendar`:

```python
from ktcalendars import KTCalendar


class ItalianCalendar(KTCalendar):
    @staticmethod
    def get_default_country_code() -> str:
        return "IT"
```

### Weekend days

Each `KTCalendar` knows which weekdays are the weekend, exposed as
`weekend_days` (numbers as per `datetime.date.weekday()`: Monday is 0,
Sunday is 6). The default is Saturday and Sunday, with built-in exceptions
for countries with a different weekend (e.g. Friday–Saturday for Egypt,
Saudi Arabia and the United Arab Emirates); pass `weekends` to override:

```python
from ktcalendars import KTCalendar

KTCalendar(country_code="EG").weekend_days  # (4, 5) — Friday and Saturday
KTCalendar(country_code="IT").weekend_days  # (5, 6) — Saturday and Sunday

cal = KTCalendar(country_code="IT", weekends=(6,))  # Sunday-only weekend
cal.get_ktday("2025-06-07").is_weekend  # False (a Saturday)
```

### Holiday calendar options

Extra keyword arguments to `KTCalendar(...)` are forwarded verbatim to
[`holidays.country_holidays`](https://pypi.org/project/holidays/)
(`years`, `expand`, `observed`, `language`, `categories`), and the
resulting holiday calendar is available as `cal.holidays`:

```python
cal = KTCalendar(country_code="IT", language="it")
cal.holidays.get("2025-06-02")  # 'Festa della Repubblica'
```

### Holiday overrides

To add holidays that are not part of the official country calendar
(e.g. company closures), implement `get_holiday_overrides` in your
configuration class. It returns a mapping of date → holiday name that is
merged on top of the holidays provided by the
[holidays](https://pypi.org/project/holidays/) package, optionally
restricted to an inclusive date range:

```python
# mypackage/config.py
import datetime

from ktcalendars import AbstractConfiguration


class CompanyConfiguration(AbstractConfiguration):
    closures = {
        datetime.date(2025, 12, 24): "Christmas Eve closure",
        datetime.date(2025, 12, 31): "New Year's Eve closure",
    }

    def get_holiday_overrides(
        self,
        country_calendar_code: str,
        from_date: datetime.date | None = None,
        to_date: datetime.date | None = None,
    ) -> dict[datetime.date, str]:
        return {
            day: name
            for day, name in self.closures.items()
            if (from_date is None or day >= from_date) and (to_date is None or day <= to_date)
        }
```

!!! note "Migrating from `EXTRA_HOLIDAY_PROVIDER`"

    The `AbstractExtraHolidayProvider` / `EXTRA_HOLIDAY_PROVIDER` mechanism
    was removed. Move the dates your provider used to flag into a
    `get_holiday_overrides` implementation on an `AbstractConfiguration`
    subclass and set `KTCALENDAR_CONFIG` instead.

## Usage

### KTDay

`KTDay` wraps a `datetime.date` and accepts another `KTDay`, a
`datetime.date`, a string (`YYYY-MM-DD`, `YYYY/MM/DD` or `YYYYMMDD`) or
`None` (today).

Every `KTDay` is bound to a `KTCalendar`: pass one with the `ktcalendar`
argument, or let the day create its own — `cal_`-prefixed keyword arguments
(e.g. `cal_country_code="IT"`) are forwarded to the `KTCalendar`
constructor, and without them the default country code is used:

```python
from ktcalendars import KTDay

day = KTDay("2025-06-02", cal_country_code="IT")
day.day_of_week      # 'Monday'
day.week_of_year     # 23
day + 7              # K2025-06-09
day - KTDay("2025-05-31")  # 2 (days)
day.is_holiday       # True (Festa della Repubblica)
day.is_workday       # False
```

See the [KTDay examples](examples/ktday.md) for more.

### KTCalendar

`KTCalendar` binds days to a country calendar, so holiday and work-day
checks need no explicit code:

```python
from ktcalendars import KTCalendar

cal = KTCalendar(country_code="IT")

day = cal.get_ktday("2025-06-02")
day.is_holiday  # True
day.is_workday  # False

# Work days between two dates (both inclusive)
cal.get_work_days("2025-06-01", "2025-06-08")
# [K2025-06-03, K2025-06-04, K2025-06-05, K2025-06-06]

# Iterate all days in a range, or in the week containing a date
list(cal.iter_dates("2025-06-01", "2025-06-03"))
cal.week_for("2025-06-04")  # (K2025-06-02, K2025-06-08)
list(cal.iter_week("2025-06-04"))

# calendar.Calendar-style month iteration, yielding KTDays
list(cal.month_weeks_days(2025, 6))  # complete weeks, includes adjacent months
list(cal.days_in_months(2025, 6))  # complete weeks, None outside the month
```

### KTDateRange

`KTDateRange` subclasses
[psycopg's `DateRange`](https://www.psycopg.org/psycopg3/docs/basic/adapt.html#range-adaptation)
and requires the `psycopg` extra (`pip install ktcalendars[psycopg]`). The
bounds accept anything a `KTDay` accepts (a `KTDay`, a `datetime.date` or a
date string), and a range can also be built from another `DateRange` or from
a `(start, end)` tuple.

Like PostgreSQL, ranges are always stored in the canonical form for discrete
types — lower bound included, upper bound excluded (`[)`). Bounds passed with
a different inclusivity are shifted by one day, and a range that
canonicalises to nothing becomes the *empty* range:

```python
from ktcalendars.ranges import KTDateRange

KTDateRange("2025-06-01", "2025-06-04")                # 2025-06-01 to 2025-06-03
KTDateRange.from_start_end("2025-06-01", "2025-06-03")  # same range, both bounds included
KTDateRange("2025-06-01", None)                        # unbounded above
KTDateRange("2025-06-01", "2025-06-01").isempty        # True — [) with equal bounds

r = KTDateRange("2025-06-01", "2025-06-04")
"2025-06-03" in r          # True
"2025-06-04" in r          # False — upper bound excluded
list(r)                    # [K2025-06-01, K2025-06-02, K2025-06-03]
```

The comparison, containment and intersection helpers accept another range or
a single day (treated as the one-day range covering it):

```python
a = KTDateRange("2025-06-01", "2025-06-10")
b = KTDateRange("2025-06-05", "2025-06-20")

a.overlap(b)               # True
a.intersection(b)          # [2025-06-05:2025-06-10)
a.contains("2025-06-05")   # True
a.fully_lt("2025-06-15")   # True — the whole range is before that day
a.precedes(b.lower)        # False;  a.precedes("2025-06-10") is True (adjacent)
a.adjacent_to(KTDateRange("2025-06-10", "2025-06-20"))  # True
```

See the [KTDateRange examples](examples/ktdaterange.md) for the full set of
helpers and the empty-range semantics.
