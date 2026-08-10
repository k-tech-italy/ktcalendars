---
title: Documentation
---

KTCalendars is a library providing utility classes for country-specific holiday-aware calendars and dates.

It builds on the [holidays](https://pypi.org/project/holidays/) package and provides:

* **`KTDay`** — a rich day object with date parsing, arithmetic, comparisons and holiday checks.
* **`KTCalendar`** — a `calendar.Calendar` subclass bound to a country calendar, with work-day and week iteration helpers.
* **`AbstractExtraHolidayProvider`** — an extension point to flag additional non-working days (e.g. company closures) via the `EXTRA_HOLIDAY_PROVIDER` environment variable.

Head over to [Getting started](usage.md) for configuration and usage, or browse the [examples](examples/ktday.md).


## Dependencies

* Python 3.10 or later


## Installation

* Install ktcalendars using your package manager of choice, e.g. Pip:
  ```bash
  pip install ktcalendars
  ```

## Bug reports and requests for enhancements

Please open an issue on the project's [issue tracker on GitHub](https://github.com/k-tech-italy/ktcalendars/issues).

## Contributing to the project

See the [contribution guide](contributing.md).

## Licensing

All rights reserved.
