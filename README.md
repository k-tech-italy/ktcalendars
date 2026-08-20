# KTcalendars

[![Test](https://github.com/k-tech-italy/ktcalendars/actions/workflows/test.yml/badge.svg)](https://github.com/k-tech-italy/ktcalendars/actions/workflows/test.yml)
[![Lint](https://github.com/k-tech-italy/ktcalendars/actions/workflows/lint.yml/badge.svg)](https://github.com/k-tech-italy/ktcalendars/actions/workflows/lint.yml)
[![Documentation](https://github.com/k-tech-italy/ktcalendars/actions/workflows/docs.yml/badge.svg)](https://github.com/k-tech-italy/ktcalendars/actions/workflows/docs.yml)
[![Pypi](https://badge.fury.io/py/ktcalendars.svg)](https://pypi.org/project/ktcalendars/)
[![codecov](https://codecov.io/github/k-tech-italy/ktcalendars/graph/badge.svg?token=BNXEW4JAYF)](https://codecov.io/github/k-tech-italy/ktcalendars)
[![security: bandit](https://img.shields.io/badge/security-bandit-yellow.svg)](https://github.com/PyCQA/bandit)

KTCalendars is a library providing utility classes for country-specific
holiday-aware calendars and dates.

It builds on the [holidays](https://pypi.org/project/holidays/) package and
provides:

* **`KTDay`** — a rich day object with date parsing, arithmetic, comparisons
  and holiday/work-day checks; every day is bound to a `KTCalendar`, and
  derived days (arithmetic results, copies) keep it.
* **`KTCalendar`** — a `calendar.Calendar` subclass bound to a country
  calendar, with configurable weekend days and work-day and week iteration
  helpers.
* **`AbstractConfiguration`** — a pluggable configuration class centralising
  holiday overrides (e.g. company closures) and the default country calendar
  code.
* **`KTDateRange`** — a calendar-aware
  [psycopg](https://pypi.org/project/psycopg/) `DateRange` subclass with
  inclusivity-aware `KTDay` iteration and rich comparison, containment and
  intersection helpers (requires the `psycopg` extra).

```python
from ktcalendars import KTCalendar

cal = KTCalendar(country_code="IT")
day = cal.get_ktday("2025-06-02")  # Festa della Repubblica
day.is_holiday                     # True
day.is_workday                     # False
cal.get_work_days("2025-06-01", "2025-06-08")
# [K2025-06-03, K2025-06-04, K2025-06-05, K2025-06-06]
```

### Day parsing, arithmetic and comparisons

```python
from ktcalendars import KTDay

day = KTDay("2025-06-02")   # also "2025/06/02", "20250602", a date, a KTDay or None (today)
day.day_of_week             # 'Monday'
day + 7                     # K2025-06-09
day - KTDay("2025-05-31")   # 2 (days)
day == "2025-06-02"         # True
list(KTDay("2025-06-01").range_to("2025-06-03"))
# [K2025-06-01, K2025-06-02, K2025-06-03]

day = KTDay("2025-06-01", cal_country_code="IT")
(day + 1).is_holiday        # True — derived days keep the calendar (2025-06-02 is an IT holiday)
```

### Weekend days per country

```python
KTCalendar(country_code="EG").weekend_days   # (4, 5) — Friday and Saturday
KTCalendar(country_code="IT").weekend_days   # (5, 6) — Saturday and Sunday

cal = KTCalendar(country_code="IT", weekends=(6,))  # Sunday-only weekend
cal.get_ktday("2025-06-07").is_weekend       # False (a Saturday)
```

### Week and month iteration

```python
cal = KTCalendar(country_code="IT")
cal.week_for("2025-06-04")           # (K2025-06-02, K2025-06-08)
list(cal.iter_week("2025-06-04"))    # the seven days of that week
list(cal.month_weeks_days(2025, 6))  # complete weeks covering June 2025
```

### Date ranges

`KTDateRange` (requires the `psycopg` extra) stores bounds as given — `[)` by
default (lower bound included, upper bound excluded) — and its helpers
normalise inclusivity internally:

```python
from ktcalendars.ranges import KTDateRange

r = KTDateRange("2025-06-01", "2025-06-04")           # upper bound excluded
list(r)                                               # [K2025-06-01, K2025-06-02, K2025-06-03]
KTDateRange.from_start_end("2025-06-01", "2025-06-03")  # both bounds included, covers the same days

"2025-06-03" in r                                     # True
r.overlap(KTDateRange("2025-06-03", "2025-06-10"))    # True
r.intersection(("2025-06-03", "2025-06-10"))          # [2025-06-03:2025-06-04)
r.precedes("2025-06-04")                              # True — adjacent, just before that day

# Ranges are calendar-aware, like KTDay
r = KTDateRange("2025-06-01", "2025-06-04", cal_country_code="IT")
[day.is_holiday for day in r]                         # [False, True, False] — days keep the calendar
```

### Company-specific holidays

Point the `KTCALENDAR_CONFIG` environment variable to a subclass of
`AbstractConfiguration` to add your own holidays on top of the official
country calendars:

```python
import datetime

from ktcalendars import AbstractConfiguration


class CompanyConfiguration(AbstractConfiguration):
    def get_holiday_overrides(self, country_calendar_code, from_date=None, to_date=None):
        return {datetime.date(2025, 12, 24): "Christmas Eve closure"}
```

```shell
export KTCALENDAR_CONFIG=mypackage.config.CompanyConfiguration
```

See the [documentation](https://k-tech-italy.github.io/ktcalendars/) for
configuration and usage, and the
[changelog](https://github.com/k-tech-italy/ktcalendars/blob/master/CHANGELOG.md)
for notable changes between releases.


## Requirements

* Python 3.10 or later


## Installation

Install ktcalendars using your package manager of choice, e.g. Pip:

```bash
pip install ktcalendars
```

To use `KTDateRange`, install the `psycopg` extra:

```bash
pip install ktcalendars[psycopg]
```

## Bug reports and requests for enhancements

Please open an issue on the project's
[issue tracker on GitHub](https://github.com/k-tech-italy/ktcalendars/issues).

## Contributing to the project

See the [contribution guide](https://github.com/k-tech-italy/ktcalendars/blob/master/CONTRIBUTING.md).

## Licensing

Licensed under the [Apache License 2.0](https://github.com/k-tech-italy/ktcalendars/blob/master/LICENSE.md).
