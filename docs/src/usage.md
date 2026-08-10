---
title: Getting started
---

# How to use ktcalendars

## Configuration

### Country calendar codes

Holiday lookups are driven by a *country calendar code*: either a plain
ISO country code (e.g. `IT`) or a country code plus subdivision separated
by a dash (e.g. `GB-ENG`, `US-CA`). Any code supported by the
[holidays](https://pypi.org/project/holidays/) package works.

The default code is resolved in this order:

1. the `country_code` passed to `KTCalendar(...)`;
2. the `DEFAULT_HOLIDAYS_CALENDAR` environment variable;
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

### Extra holidays

To flag additional non-working days that are not part of the official
country calendar (e.g. company closures), subclass
`AbstractExtraHolidayProvider` and set the `EXTRA_HOLIDAY_PROVIDER`
environment variable to the fully qualified name of your subclass
before `ktcalendars` is imported:

```python
# mypackage/closures.py
from ktcalendars import providers


class CompanyClosures(providers.AbstractExtraHolidayProvider):
    @classmethod
    def is_extra_holiday(cls, ktd, country_calendar_code: str) -> bool:
        return (ktd.month, ktd.day) == (12, 24)  # Christmas Eve closure
```

```shell
export EXTRA_HOLIDAY_PROVIDER=mypackage.closures.CompanyClosures
```

When the variable is unset, the default `NoExtraHolidayProvider` is used,
which never reports extra holidays.

## Usage

### KTDay

`KTDay` wraps a `datetime.date` and accepts another `KTDay`, a
`datetime.date`, a string (`YYYY-MM-DD`, `YYYY/MM/DD` or `YYYYMMDD`) or
`None` (today):

```python
from ktcalendars import KTDay

day = KTDay("2025-06-02")
day.day_of_week      # 'Monday'
day.week_of_year     # 23
day + 7              # K2025-06-09
day - KTDay("2025-05-31")  # 2 (days)
day.is_holiday("IT")       # True (Festa della Repubblica)
```

See the [KTDay examples](examples/ktday.md) for more.

### KTCalendar

`KTCalendar` binds days to a country calendar, so holiday checks need no
explicit code:

```python
from ktcalendars import KTCalendar

cal = KTCalendar(country_code="IT")

day = cal.get_ktday("2025-06-02")
day.is_holiday()  # True
day.is_non_working_day()  # True

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
