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

## Holiday checks

Without an explicit country calendar code, the default one is used
(see [Getting started](../usage.md#configuration)):

```python
KTDay("2025-06-02").is_holiday("IT")          # True (Festa della Repubblica)
KTDay("2025-06-02").is_holiday("GB-ENG")      # False
KTDay("2025-06-07").is_non_working_day("IT")  # True (Saturday)
```
