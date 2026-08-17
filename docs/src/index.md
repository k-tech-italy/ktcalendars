---
title: Documentation
---

KTCalendars is a library providing utility classes for country-specific holiday-aware calendars and dates.

It builds on the [holidays](https://pypi.org/project/holidays/) package and provides:

* **`KTDay`** — a rich day object with date parsing, arithmetic, comparisons and holiday/work-day checks; every day is bound to a `KTCalendar`, and derived days (arithmetic results, copies) keep it.
* **`KTCalendar`** — a `calendar.Calendar` subclass bound to a country calendar, with configurable weekend days and work-day and week iteration helpers.
* **`AbstractConfiguration`** — a pluggable configuration class, selected via the `KTCALENDAR_CONFIG` environment variable, centralising holiday overrides (e.g. company closures) and the default country calendar code.
* **`KTDateRange`** — a calendar-aware [psycopg](https://pypi.org/project/psycopg/) `DateRange` subclass with PostgreSQL-canonical `[)` bounds, `KTDay` iteration and rich comparison, containment and intersection helpers (requires the `psycopg` extra).

Head over to [Getting started](usage.md) for configuration and usage, or browse the [examples](examples/ktday.md).


## Dependencies

* Python 3.10 or later


## Installation

* Install ktcalendars using your package manager of choice, e.g. Pip:
  ```bash
  pip install ktcalendars
  ```
* To use `KTDateRange`, install the `psycopg` extra:
  ```bash
  pip install ktcalendars[psycopg]
  ```

## Bug reports and requests for enhancements

Please open an issue on the project's [issue tracker on GitHub](https://github.com/k-tech-italy/ktcalendars/issues).

## Contributing to the project

See the [contribution guide](contributing.md).

## Licensing

Licensed under the [Apache License 2.0](https://github.com/k-tech-italy/ktcalendars/blob/master/LICENSE.md).
