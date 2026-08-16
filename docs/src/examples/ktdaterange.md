# KTDateRange

Example usages of `KTDateRange`, a
[psycopg `DateRange`](https://www.psycopg.org/psycopg3/docs/basic/adapt.html#range-adaptation)
subclass. It requires the `psycopg` extra:

```bash
pip install ktcalendars[psycopg]
```

```python
import datetime

from psycopg.types.range import DateRange

from ktcalendars.days import KTDay
from ktcalendars.ranges import KTDateRange
```

## Creation

Bounds accept anything a `KTDay` accepts — a `KTDay`, a `datetime.date` or a
date string — plus `None` for an unbounded side. A range can also be built
from another `DateRange` or from a `(start, end)` tuple:

```python
KTDateRange("2025-06-01", "2025-06-04")        # 2025-06-01 to 2025-06-03
KTDateRange(datetime.date(2025, 6, 1), KTDay("2025-06-04"))
KTDateRange(("2025-06-01", "2025-06-04"))      # from a tuple
KTDateRange(DateRange(datetime.date(2025, 6, 1), datetime.date(2025, 6, 4)))
KTDateRange("2025-06-01", None)                # unbounded above
KTDateRange()                                  # unbounded on both sides
KTDateRange(empty=True)                        # the empty range
```

`from_start_end` builds a range where **both** dates are included:

```python
KTDateRange.from_start_end("2025-06-01", "2025-06-03")
# [2025-06-01:2025-06-04) — covers the 1st, 2nd and 3rd
```

The lower bound may not be after the upper bound:

```python
KTDateRange("2025-06-04", "2025-06-01")  # ValueError
```

## Canonical form

Like PostgreSQL, ranges are always stored in the canonical form for discrete
types: lower bound included, upper bound excluded (`[)`). Bounds passed with
a different inclusivity are shifted by one day, and a range that
canonicalises to nothing becomes the *empty* range:

```python
KTDateRange("2025-06-01", "2025-06-10", bounds="[]")
# [2025-06-01:2025-06-11)

KTDateRange("2025-06-01", "2025-06-10", bounds="()")
# [2025-06-02:2025-06-10)

KTDateRange("2025-06-01", "2025-06-01").isempty  # True — [) with equal bounds
```

## Membership and iteration

`in` accepts anything a `KTDay` accepts; iteration yields `KTDay`s
(the excluded upper bound is not yielded):

```python
r = KTDateRange("2025-06-01", "2025-06-04")

"2025-06-03" in r                  # True
datetime.date(2025, 6, 4) in r     # False — upper bound excluded
list(r)                            # [K2025-06-01, K2025-06-02, K2025-06-03]

r.boundaries                       # (datetime.date(2025, 6, 1), datetime.date(2025, 6, 4))
str(r)                             # '[2025-06-01:2025-06-04)'
str(KTDateRange("2025-06-01", None))  # '[2025-06-01:...)'

list(KTDateRange("2025-06-01", None))  # TypeError — cannot iterate an unbounded range
list(KTDateRange(empty=True))          # []
```

## Comparisons

Every helper accepts another range (a `KTDateRange` or any `DateRange`) or a
single day, treated as the one-day range covering it:

```python
a = KTDateRange("2025-06-01", "2025-06-10")
b = KTDateRange("2025-06-05", "2025-06-20")

a.fully_lt("2025-06-10")   # True — the whole range is before that day
a.fully_lt(b)              # False — they overlap
a.fully_gt("2025-05-31")   # True — the whole range is after that day

a.startsbefore(b)          # True
b.startsafter(a)           # True
a.endsbefore(b)            # True
b.endsafter(a)             # True
```

`precedes`, `follows` and `adjacent_to` check that two ranges touch at a
boundary without overlapping:

```python
c = KTDateRange("2025-06-10", "2025-06-20")

a.precedes(c)       # True — a ends exactly where c starts
c.follows(a)        # True
a.adjacent_to(c)    # True
a.precedes("2025-06-10")  # True — adjacent to that day
```

## Containment, overlap and intersection

```python
a = KTDateRange("2025-06-01", "2025-06-10")
b = KTDateRange("2025-06-05", "2025-06-20")

a.contains("2025-06-05")                          # True
a.contains(KTDateRange("2025-06-02", "2025-06-05"))  # True
KTDateRange("2025-06-02", "2025-06-05").contained_by(a)  # True

a.overlap(b)               # True
a.overlap(KTDateRange("2025-06-10", "2025-06-20"))  # False — adjacent, not overlapping

a.intersection(b)          # [2025-06-05:2025-06-10)
a.intersection("2025-06-05")  # [2025-06-05:2025-06-06)
a.intersection(KTDateRange("2025-06-25", None))  # None — no overlap
```

`as_dates` returns a copy with infinite boundaries replaced by
`datetime.date.min` / `datetime.date.max`:

```python
KTDateRange("2025-06-01", None).as_dates().upper  # datetime.date.max
```

## The empty range

Following PostgreSQL semantics, the empty range overlaps, precedes and
follows nothing, contains only itself, and is contained by every range:

```python
empty = KTDateRange(empty=True)
a = KTDateRange("2025-06-01", "2025-06-10")

str(empty)             # 'empty'
a.overlap(empty)       # False
a.contains(empty)      # True
empty.contains(a)      # False
empty.contained_by(a)  # True
a.adjacent_to(empty)   # False
a.intersection(empty)  # None
```
