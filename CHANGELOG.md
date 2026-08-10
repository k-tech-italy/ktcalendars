# Changelist

Notable changes to ktcalendars, newest first.

## 1.0.0 (2026-08-10)

### Breaking changes !!

* The `ExtraHolidayProvider` extension point was replaced by
  `AbstractExtraHolidayProvider` (the abstract base class to subclass) and
  `NoExtraHolidayProvider` (the default implementation, which never reports
  extra holidays). Custom providers are now configured by setting the
  `EXTRA_HOLIDAY_PROVIDER` environment variable to the fully qualified name
  of the subclass, instead of reassigning `providers.extra_holiday_provider`.
* `KTCalendar.itermonthktdates` and `KTCalendar.itermonthktdays` were renamed
  to `month_weeks_days` and `days_in_months`.
* The package was split into `calendar`, `days`, `providers` and `utils`
  modules. `KTCalendar` and `KTDay` are still importable from `ktcalendars`
  directly.

### Changed

* Adding an unsupported type to a `KTDay` now raises `TypeError` instead of
  an obscure `UnboundLocalError`.
* Stricter typing throughout the public API, with module docstrings and
  explicit `__all__` declarations.

### Internal

* Test suite extended to 100% line and branch coverage.
* Lint runs through pre-commit in tox, with strict mypy checked against typed
  dependencies; tests run on Python 3.10–3.14 and enforce 100% diff coverage.

  
## 0.9.1 (2025-10-22)

* Added calendar-aware `KTDay` generators to `KTCalendar` (`get_ktday`,
  work/non-work day and week iteration helpers).
* Fixed subclasses of `KTCalendar` being unable to use an overridden
  `get_default_country_code`.
* Added `KTDay` usage examples to the documentation.

### Docs

- **Examples**: Added KTDay examples

## 0.8.1 (2025-10-15)

* First full working release: `KTDay` date parsing, arithmetic, comparisons
  and holiday checks; `KTCalendar` bound to a country calendar code, driven
  by the [holidays](https://pypi.org/project/holidays/) package.

### Fix

- **KTCalendar**: Fix child class of KTCalendar unable to use the overriden get_default_country_code

## 0.8.0 (2025-10-15)

### Feat

- **Full-release**: First full working release
