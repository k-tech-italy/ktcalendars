# KTDay

Example usages of `KTDay`.

```python
import datetime

from ktcalendars import KTDay
from ktcalendars.utils import dt
```

## Creation

A `KTDay` can be created from a string, a `datetime.date`, another `KTDay`
or nothing at all (today):

```python
KTDay("2025-06-02")
KTDay("2025/06/02")
KTDay("20250602")
KTDay(datetime.date(2025, 6, 2))
KTDay(KTDay("2025-06-02"))
KTDay()  # today
```

## Properties

```python
day = KTDay("2025-06-02")

day.day                # 2
day.month              # 6
day.year               # 2025
day.day_of_year        # 153
day.week_of_year       # 23
day.day_of_week        # 'Monday'
day.day_of_week_short  # 'Mon'
day.month_name         # 'June'
day.month_name_short   # 'Jun'
```

## Comparison

You can compare a KTDay with another KTDay, a date or a date string:

```python
KTDay("2025-06-02") == KTDay("2025-06-02")           # True
KTDay("2025-06-02") != KTDay("2025-06-03")           # True
KTDay("2025-06-02") == dt("2025-06-02")              # True
KTDay("2025-06-02") == "2025-06-02"                  # True

KTDay("2025-06-03") > KTDay("2025-06-02")            # True
KTDay("2025-06-02") >= KTDay("2025-06-02")           # True
KTDay("2025-06-01") >= KTDay("2025-06-02")           # False
KTDay("2025-06-03") > datetime.date(2025, 6, 2)      # True
KTDay("2025-06-01") < datetime.date(2025, 6, 2)      # True
```

## Arithmetic

Adding an `int` (days), `datetime.timedelta` or
`dateutil.relativedelta.relativedelta` returns a new `KTDay`; subtracting
another day returns the number of days between the two:

```python
from dateutil.relativedelta import relativedelta

KTDay("2025-06-02") + 7                            # K2025-06-09
KTDay("2025-06-02") - 1                            # K2025-06-01
KTDay("2025-06-02") + datetime.timedelta(days=3)   # K2025-06-05
KTDay("2025-06-02") + relativedelta(months=1)      # K2025-07-02
KTDay("2025-06-05") - KTDay("2025-06-02")          # 3
```

## Ranges

```python
list(KTDay("2025-06-01").range_to("2025-06-03"))
# [K2025-06-01, K2025-06-02, K2025-06-03]
```

## Holiday and work-day checks

Every `KTDay` is bound to a `KTCalendar` which drives these checks:
`cal_`-prefixed keyword arguments are forwarded to the `KTCalendar`
constructor, and without them the default country calendar code is used
(see [Getting started](../usage.md#configuration)):

```python
KTDay("2025-06-02", cal_country_code="IT").is_holiday      # True (Festa della Repubblica)
KTDay("2025-06-02", cal_country_code="GB-ENG").is_holiday  # False
KTDay("2025-06-07").is_weekend                             # True (Saturday)
KTDay("2025-06-07").is_workday                             # False
KTDay("2025-06-02", cal_country_code="IT").is_workday      # False (holiday)
```

`is_workday` is True when the day is not a weekend day, not a holiday and
not an extra holiday; `is_extra_holiday` checks the configuration's
[holiday overrides](../usage.md#holiday-overrides).
