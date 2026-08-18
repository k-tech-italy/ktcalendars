# Changelist

Notable changes to ktcalendars, newest first.

## 3.3.1 (2026-08-19)

### Fix

- **DateRange.as_dates**: Fixes wrong return of the method: now returns a tuple[datetime.date, datetime.date]

## 3.3.0 (2026-08-18)

### Feat

- **ranges**: add KTDateRange.gaps to find uncovered periods in a window

## 3.2.0 (2026-08-17)

### Feat

- **calendar-awareness**: KTDay derived days and KTDateRange keep their KTCalendar

## 3.1.1 (2026-08-16)

### Fix

- **versioning**: Fixing versioning

## 3.1.0 (2026-08-16)

### Feat

- **KTDateRange-with-psycopg**: Introduced KTDateRange with optional psycopg dependency

### Fix

- **Documentation**: Improved docs and README

## 3.0.0 (2026-08-12)

### BREAKING CHANGE

- `KTDay.is_holiday` and `KTDay.is_extra_holiday` are now read-only
  properties: they no longer accept a country calendar code or the
  `include_sundays_as_holiday` flag. The country code comes from the
  `KTCalendar` the day is bound to, and Sundays are covered by the new
  `is_weekend` property.
- `KTDay.is_non_working_day()` was removed: use the new `is_workday`
  property (note the inverted meaning), or `is_weekend` / `is_holiday` /
  `is_extra_holiday` for the individual conditions.
- Every `KTDay` is now bound to a `KTCalendar`: one is created when none is
  passed, and `cal_`-prefixed keyword arguments (e.g.
  `cal_country_code="IT"`) are forwarded to the `KTCalendar` constructor.

### Feat

- `KTCalendar` accepts a `weekends` tuple of weekday numbers (Monday is 0),
  defaulting per country (e.g. Friday–Saturday for EG, SA and AE), exposed
  as `weekend_days` and used by `KTDay.is_weekend` / `is_workday`.
- `KTCalendar` forwards holiday options (`years`, `expand`, `observed`,
  `language`, `categories`) to `holidays.country_holidays` and exposes the
  resulting holiday calendar as `cal.holidays`.

### Fix

- **mypy-typing**: `Unpack` is imported from `typing_extensions` so the
  package works on Python 3.10.

## 2.0.0 (2026-08-11)

### BREAKING CHANGE

- The `AbstractExtraHolidayProvider` / `EXTRA_HOLIDAY_PROVIDER` mechanism was
  removed (`ktcalendars.providers` no longer exists and the
  `EXTRA_HOLIDAY_PROVIDER` environment variable is no longer read). Extra
  holidays are now provided by the configuration class: migrate your provider
  subclass to an `AbstractConfiguration` subclass exposing the same dates via
  `get_holiday_overrides`, and set `KTCALENDAR_CONFIG` instead.

### Feat

- **config**: new pluggable configuration class (Req 001): set the
  `KTCALENDAR_CONFIG` environment variable to the fully qualified name of an
  `AbstractConfiguration` subclass to centralise holiday overrides and the
  default country calendar code. The configuration is loaded lazily and
  cached; `ktcalendars.config.reset_configuration()` reloads it.
- The default country calendar code is now resolved from the new
  `KTCALENDAR_COUNTRY` environment variable, falling back to the deprecated
  `DEFAULT_HOLIDAYS_CALENDAR` one (which now emits a `DeprecationWarning`)
  and finally to `GB-ENG`.

### Fix

- **cz**: read the current version from SCM tags

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
