import datetime
import pickle
import typing
from contextlib import nullcontext as does_not_raise

import pytest
from psycopg.types.range import DateRange

from ktcalendars.calendar import KTCalendar
from ktcalendars.days import KTDay
from ktcalendars.ranges import KTDateRange
from ktcalendars.types import KTDayType
from ktcalendars.utils import dt


def test_ktdaytype_alias():
    assert typing.get_args(KTDayType) == (KTDay, datetime.date, str)


param_order = pytest.raises(ValueError, match='Lower bound must be smaller than upper bound')
ok = does_not_raise()
non_iterable = pytest.raises(TypeError, match='Cannot iterate over unbounded range')


def test_boundaries():
    period = KTDateRange('2026-01-01', '2026-01-31')
    assert tuple(x for x in period.boundaries) == (dt('2026-01-01'), dt('2026-01-31'))


@pytest.mark.parametrize(
    'period, expectation, result',
    [
        pytest.param(('2026-01-01', '2026-01-03'), ok, ['2026-01-01', '2026-01-02'], id='ok'),
        pytest.param((None, '2026-01-03'), non_iterable, None, id='none-start'),
        pytest.param(('2026-01-01', None), non_iterable, None, id='none-end'),
        pytest.param((datetime.date.min, '2026-01-03'), non_iterable, None, id='min-start'),
        pytest.param(('2026-01-01', datetime.date.max), non_iterable, None, id='max-end'),
    ],
)
def test_iterate(period, expectation, result):
    kdr = KTDateRange(*period)
    with expectation:
        assert list(kdr) == result


@pytest.mark.parametrize(
    'period, expectation, bounds, isempty',
    [
        pytest.param(
            ('2026-01-01', dt('2026-01-31')),
            ok,
            (dt('2026-01-01'), dt('2026-01-31')),
            False,
            id='simple',
        ),
        pytest.param((dt('2026-01-01'), None), ok, (dt('2026-01-01'), None), False, id='none-end'),
        pytest.param(
            (KTDay('2026-01-01'), datetime.date.max),
            ok,
            (dt('2026-01-01'), datetime.date.max),
            False,
            id='max-end',
        ),
        pytest.param((None, '2026-01-01'), ok, (None, dt('2026-01-01')), False, id='none-start'),
        pytest.param((None,), ok, (None, None), False, id='one'),
        pytest.param((), ok, (None, None), False, id='empty'),
        pytest.param(
            (datetime.date.min, datetime.date.max),
            ok,
            (datetime.date.min, datetime.date.max),
            False,
            id='min-max',
        ),
        pytest.param(('2026-02-03', '2026-02-01'), param_order, None, False, id='order'),
        pytest.param(('2026-02-01', '2026-02-01'), ok, (None, None), True, id='equal-bounds-empty'),
        pytest.param((('2026-01-01', '2026-01-31'),), ok, (dt('2026-01-01'), dt('2026-01-31')), False, id='tuple'),
    ],
)
def test_instance_creation(period, expectation, bounds, isempty):
    with expectation:
        dr = KTDateRange(*period)
        assert dr is not None
        assert (dr.lower, dr.upper) == bounds
        assert dr.isempty is isempty


@pytest.mark.parametrize(
    'period, other, result',
    [
        pytest.param(('2026-01-01', '2026-01-31'), ('2026-02-01', None), True, id='fully-lt'),
        pytest.param(('2026-01-01', '2026-02-02'), ('2026-02-01', '2026-02-10'), False, id='overlap-lower'),
    ],
)
def test_fully_before(period, other, result):
    assert KTDateRange(*period).fully_lt(KTDateRange(*other)) is result


@pytest.mark.parametrize(
    'period, other, result',
    [
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-01-01', '2026-01-31'), True, id='fully-gt'),
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-01-01', None), False, id='open-ended'),
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-01-01', '2026-02-02'), False, id='overlap-upper'),
    ],
)
def test_fully_after(period, other, result):
    assert KTDateRange(*period).fully_gt(KTDateRange(*other)) is result


@pytest.mark.parametrize(
    'period, other, before, after',
    [
        pytest.param(('2026-01-01', None), ('2026-01-01', None), False, False, id='lower-equal'),
        pytest.param(('2026-01-01', None), ('2026-01-02', None), True, False, id='lower-lt'),
        pytest.param(('2026-01-02', None), ('2026-01-01', None), False, True, id='lower-gt'),
    ],
)
def test_start_comparison(period, other, before: bool, after: bool):
    assert KTDateRange(*period).startsbefore(KTDateRange(*other)) is before
    assert KTDateRange(*period).startsafter(KTDateRange(*other)) is after


@pytest.mark.parametrize(
    'period, other, before, after',
    [
        pytest.param(('2026-01-01', '2026-01-10'), ('2026-01-02', '2026-01-10'), False, False, id='equal'),
        pytest.param(('2026-01-01', None), ('2026-01-02', None), False, False, id='equal-none'),
        pytest.param(('2026-01-01', None), ('2026-01-01', '2026-01-10'), False, True, id='none'),
        pytest.param(('2026-01-01', '2026-01-10'), ('2026-01-01', '2026-01-11'), True, False, id='lower'),
        pytest.param(('2026-01-01', '2026-01-10'), ('2026-01-01', '2026-01-09'), False, True, id='higher'),
    ],
)
def test_end_comparison(period, other, before: bool, after: bool):
    assert KTDateRange(*period).endsbefore(KTDateRange(*other)) is before
    assert KTDateRange(*period).endsafter(KTDateRange(*other)) is after


@pytest.mark.parametrize(
    'period, other, result',
    [
        pytest.param(('2026-01-01', '2026-02-01'), ('2026-02-01', '2026-02-10'), True, id='precedes'),
        pytest.param(('2026-01-01', '2026-01-31'), ('2026-02-02', '2026-02-10'), False, id='gap-left'),
        pytest.param(('2026-01-01', None), ('2026-02-01', '2026-02-10'), False, id='none'),
    ],
)
def test_precedes(period, other, result):
    assert KTDateRange(*period).precedes(KTDateRange(*other)) is result


@pytest.mark.parametrize(
    'period, other, result',
    [
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-01-01', '2026-02-01'), True, id='succeeds'),
        pytest.param(('2026-02-02', '2026-02-28'), ('2026-01-02', '2026-01-31'), False, id='gap-right'),
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-01-01', None), False, id='none'),
    ],
)
def test_succeed(period, other, result):
    assert KTDateRange(*period).follows(KTDateRange(*other)) is result


@pytest.mark.parametrize(
    'period, day, result',
    [
        pytest.param(('2026-02-01', '2026-02-28'), '2026-02-01', True, id='in'),
        pytest.param(('2026-02-02', '2026-02-28'), '2026-02-01', False, id='left'),
        pytest.param(('2026-02-01', '2026-02-28'), '2026-02-28', False, id='right'),
        pytest.param(('2026-02-01', None), '2026-02-28', True, id='none'),
    ],
)
def test_includes(period, day, result):
    assert (dt(day) in KTDateRange(*period)) is result


@pytest.mark.parametrize(
    'period, other, result',
    [
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-02-01', '2026-02-28'), True, id='same'),
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-01-31', '2026-02-28'), False, id='left'),
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-02-01', '2026-03-01'), False, id='right'),
        pytest.param((None, '2026-02-28'), ('2026-02-01', '2026-02-28'), True, id='self-lower-None'),
        pytest.param(('2026-02-01', None), ('2026-02-01', '2026-02-28'), True, id='self-upper-none'),
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-02-01', None), False, id='other-upper-none'),
    ],
)
def test_contains(period, other, result):
    assert KTDateRange(*period).contains(KTDateRange(*other)) is result


@pytest.mark.parametrize(
    'period, other, result',
    [
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-02-01', '2026-02-28'), True, id='same'),
        pytest.param(('2026-02-05', '2026-02-20'), ('2026-02-01', '2026-02-28'), True, id='inside'),
        pytest.param(('2026-02-01', '2026-02-20'), ('2026-02-01', '2026-02-28'), True, id='same-lower'),
        pytest.param(('2026-02-05', '2026-02-28'), ('2026-02-01', '2026-02-28'), True, id='same-upper'),
        pytest.param(('2026-01-31', '2026-02-20'), ('2026-02-01', '2026-02-28'), False, id='wider-left'),
        pytest.param(('2026-02-05', '2026-03-01'), ('2026-02-01', '2026-02-28'), False, id='wider-right'),
        pytest.param(('2026-01-31', '2026-03-01'), ('2026-02-01', '2026-02-28'), False, id='wider-both'),
        pytest.param(('2026-02-01', None), ('2026-02-01', '2026-02-28'), False, id='self-upper-none'),
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-02-01', None), True, id='other-upper-none'),
        pytest.param((None, '2026-02-28'), ('2026-02-01', '2026-02-28'), False, id='self-lower-none'),
        pytest.param(('2026-02-01', '2026-02-28'), (None, '2026-02-28'), True, id='other-lower-none'),
        pytest.param((None, '2026-02-28'), (None, '2026-02-28'), True, id='both-lower-none'),
    ],
)
def test_contained_by(period, other, result):
    assert KTDateRange(*period).contained_by(KTDateRange(*other)) is result


@pytest.mark.parametrize(
    'period, day, result',
    [
        pytest.param(('2026-02-01', '2026-03-01'), '2026-02-01', True, id='lower'),
        pytest.param(('2026-02-01', '2026-03-01'), dt('2026-02-28'), True, id='upper'),
        pytest.param(('2026-02-01', '2026-03-01'), KTDay('2026-01-31'), False, id='lower-'),
        pytest.param(('2026-02-01', '2026-03-01'), '2026-03-01', False, id='upper+'),
    ],
)
def test_in(period, day, result):
    assert (day in KTDateRange(*period)) is result


@pytest.mark.parametrize(
    'period, other, result',
    [
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-02-01', '2026-02-28'), True, id='same'),
        pytest.param(('2026-02-05', '2026-02-20'), ('2026-02-01', '2026-02-28'), True, id='self-inside-other'),
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-02-05', '2026-02-20'), True, id='other-inside-self'),
        pytest.param(('2026-02-01', '2026-02-15'), ('2026-01-15', '2026-02-28'), True, id='self-lower-in-other'),
        pytest.param(('2026-01-15', '2026-02-28'), ('2026-02-01', '2026-02-15'), True, id='other-upper-in-self'),
        pytest.param(('2026-02-01', None), ('2026-02-01', '2026-02-28'), True, id='self-upper-none'),
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-02-01', None), True, id='other-upper-none'),
        pytest.param(('2026-01-01', '2026-01-31'), ('2026-02-01', '2026-02-28'), False, id='gap'),
        pytest.param(('2026-01-01', '2026-02-01'), ('2026-02-01', '2026-02-28'), False, id='adjacent'),
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-01-01', '2026-02-01'), False, id='adjacent-reversed'),
    ],
)
def test_overlaps(period, other, result):
    assert KTDateRange(*period).overlap(KTDateRange(*other)) is result


@pytest.mark.parametrize(
    'period, other, result',
    [
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-02-28', '2026-03-15'), True, id='self-precedes-other'),
        pytest.param(('2026-02-28', '2026-03-15'), ('2026-02-01', '2026-02-28'), True, id='self-follows-other'),
        pytest.param(('2026-01-01', '2026-02-01'), ('2026-02-01', '2026-02-28'), True, id='adjacent-boundary'),
        pytest.param(('2026-01-01', '2026-01-31'), ('2026-02-01', '2026-02-28'), False, id='gap'),
        pytest.param(('2026-01-01', '2026-02-01'), ('2026-02-02', '2026-02-28'), False, id='not-adjacent-gap'),
        pytest.param(('2026-02-01', '2026-02-28'), ('2026-02-01', '2026-02-28'), False, id='same-not-adjacent'),
    ],
)
def test_adjacent_to(period, other, result):
    assert KTDateRange(*period).adjacent_to(KTDateRange(*other)) is result


@pytest.mark.parametrize(
    'period, result',
    [
        pytest.param(('2026-02-01', '2026-02-28'), '[2026-02-01:2026-02-28)', id='ok'),
        pytest.param((None, '2026-02-28'), '(...:2026-02-28)', id='none-start'),
        pytest.param(('2026-02-01', None), '[2026-02-01:...)', id='none-end'),
        pytest.param((datetime.date.min, '2026-02-28'), '(...:2026-02-28)', id='inf-start'),
        pytest.param(('2026-02-01', datetime.date.max), '[2026-02-01:...)', id='inf-end'),
        pytest.param(('2026-02-01', '2026-02-01'), 'empty', id='empty'),
    ],
)
def test_str(period, result):
    res = str(KTDateRange(*period))
    assert res == result, f'Expected {result}, got {res}'


@pytest.mark.parametrize(
    'period, bounds, canonical, isempty',
    [
        pytest.param(('2026-01-01', '2026-01-10'), '[]', (dt('2026-01-01'), dt('2026-01-11')), False, id='incl-upper'),
        pytest.param(('2026-01-01', '2026-01-10'), '()', (dt('2026-01-02'), dt('2026-01-10')), False, id='excl-lower'),
        pytest.param(('2026-01-01', '2026-01-10'), '(]', (dt('2026-01-02'), dt('2026-01-11')), False, id='excl-incl'),
        pytest.param(('2026-01-01', '2026-01-01'), '[]', (dt('2026-01-01'), dt('2026-01-02')), False, id='one-day'),
        pytest.param(('2026-01-01', '2026-01-01'), '()', (None, None), True, id='excl-equal-empty'),
        pytest.param(('2026-01-01', '2026-01-02'), '()', (None, None), True, id='excl-adjacent-empty'),
        pytest.param((None, '2026-01-10'), '(]', (None, dt('2026-01-11')), False, id='unbounded-lower'),
    ],
)
def test_canonicalisation(period, bounds, canonical, isempty):
    """Any bound inclusivity is normalised to [) like PostgreSQL does for discrete ranges."""
    dr = KTDateRange(period[0], period[1], bounds=bounds)
    assert dr.boundaries == canonical
    assert dr.isempty is isempty
    assert not dr.upper_inc
    assert dr.lower_inc is (dr.lower is not None)


def test_invalid_bounds():
    with pytest.raises(ValueError, match='bound flags not valid'):
        KTDateRange('2026-01-01', '2026-01-10', bounds='[x')


@pytest.mark.parametrize(
    'source, canonical, isempty',
    [
        pytest.param(
            DateRange(dt('2026-01-01'), dt('2026-01-10'), '[]'),
            (dt('2026-01-01'), dt('2026-01-11')),
            False,
            id='daterange-incl',
        ),
        pytest.param(
            DateRange(dt('2026-01-01'), dt('2026-01-10')), (dt('2026-01-01'), dt('2026-01-10')), False, id='daterange'
        ),
        pytest.param(DateRange(empty=True), (None, None), True, id='daterange-empty'),
        pytest.param(
            KTDateRange('2026-01-01', '2026-01-10'), (dt('2026-01-01'), dt('2026-01-10')), False, id='ktdaterange'
        ),
    ],
)
def test_copy_constructor(source, canonical, isempty):
    dr = KTDateRange(source)
    assert dr.boundaries == canonical
    assert dr.isempty is isempty


def test_from_start_end():
    dr = KTDateRange.from_start_end('2026-01-01', '2026-01-03')
    assert dr.boundaries == (dt('2026-01-01'), dt('2026-01-04'))
    assert list(dr) == ['2026-01-01', '2026-01-02', '2026-01-03']
    assert '2026-01-03' in dr
    assert '2026-01-04' not in dr


def test_from_start_end_one_day():
    dr = KTDateRange.from_start_end('2026-01-01', '2026-01-01')
    assert not dr.isempty
    assert list(dr) == ['2026-01-01']


def test_from_start_end_reversed():
    with pytest.raises(ValueError, match='Lower bound must be smaller than upper bound'):
        KTDateRange.from_start_end('2026-01-03', '2026-01-01')


def test_fully_lt_with_inclusive_upper():
    """Regression: a [] range is not fully before a day it contains."""
    dr = KTDateRange.from_start_end('2026-01-01', '2026-01-10')
    assert '2026-01-10' in dr
    assert dr.fully_lt('2026-01-10') is False
    assert dr.fully_lt('2026-01-11') is True


def test_contains_with_inclusive_upper():
    """Regression: a [) range does not contain the [] range ending on its excluded upper bound."""
    half_open = KTDateRange('2026-01-01', '2026-01-10')
    closed = KTDateRange.from_start_end('2026-01-01', '2026-01-10')
    assert half_open.contains(closed) is False
    assert closed.contains(half_open) is True


@pytest.mark.parametrize(
    'period, day, fully_lt, fully_gt, contains, precedes',
    [
        pytest.param(('2026-02-01', '2026-02-10'), '2026-02-10', True, False, False, True, id='day-at-upper'),
        pytest.param(('2026-02-01', '2026-02-10'), '2026-02-05', False, False, True, False, id='day-inside'),
        pytest.param(('2026-02-01', '2026-02-10'), '2026-01-31', False, True, False, False, id='day-before'),
        pytest.param(('2026-02-01', '2026-02-10'), dt('2026-02-11'), True, False, False, False, id='date-after-upper'),
        pytest.param(('2026-02-01', '2026-02-10'), KTDay('2026-02-01'), False, False, True, False, id='ktday-at-lower'),
    ],
)
def test_single_day_other(period, day, fully_lt, fully_gt, contains, precedes):
    """A single day passed as `other` behaves as the one-day range covering it."""
    dr = KTDateRange(*period)
    assert dr.fully_lt(day) is fully_lt
    assert dr.fully_gt(day) is fully_gt
    assert dr.contains(day) is contains
    assert dr.precedes(day) is precedes


def test_empty_semantics():
    """The empty range overlaps/precedes/follows nothing, is contained by everything and contains only itself."""
    empty = KTDateRange(empty=True)
    dr = KTDateRange('2026-01-01', '2026-01-10')
    assert dr.overlap(empty) is False
    assert empty.overlap(dr) is False
    assert dr.contains(empty) is True
    assert empty.contains(dr) is False
    assert empty.contains(empty) is True
    assert empty.contained_by(dr) is True
    assert dr.fully_lt(empty) is False
    assert empty.fully_gt(dr) is False
    assert dr.adjacent_to(empty) is False
    assert dr.startsbefore(empty) is False
    assert empty.startsafter(dr) is False
    assert dr.endsbefore(empty) is False
    assert empty.endsafter(dr) is False
    assert dr.intersection(empty) is None
    assert list(empty) == []
    assert '2026-01-01' not in empty
    assert str(empty) == 'empty'


@pytest.mark.parametrize(
    'period, other, result',
    [
        pytest.param(
            ('2026-01-01', '2026-01-20'),
            ('2026-01-10', '2026-01-31'),
            (dt('2026-01-10'), dt('2026-01-20')),
            id='overlapping',
        ),
        pytest.param(
            ('2026-01-10', '2026-01-31'),
            ('2026-01-01', '2026-01-20'),
            (dt('2026-01-10'), dt('2026-01-20')),
            id='overlapping-reversed',
        ),
        pytest.param(
            ('2026-01-01', '2026-01-31'),
            ('2026-01-10', '2026-01-20'),
            (dt('2026-01-10'), dt('2026-01-20')),
            id='inside',
        ),
        pytest.param(('2026-01-01', '2026-01-10'), ('2026-01-20', '2026-01-31'), None, id='disjoint'),
        pytest.param(('2026-01-01', '2026-01-10'), ('2026-01-10', '2026-01-31'), None, id='adjacent'),
        pytest.param((None, '2026-01-20'), ('2026-01-10', None), (dt('2026-01-10'), dt('2026-01-20')), id='unbounded'),
        pytest.param((None, '2026-01-20'), (None, '2026-01-10'), (None, dt('2026-01-10')), id='unbounded-kept-open'),
        pytest.param(('2026-01-01', '2026-01-10'), '2026-01-05', (dt('2026-01-05'), dt('2026-01-06')), id='single-day'),
    ],
)
def test_intersection(period, other, result):
    intersection = KTDateRange(*period).intersection(KTDateRange(*other) if isinstance(other, tuple) else other)
    if result is None:
        assert intersection is None
    else:
        assert intersection is not None
        assert intersection.boundaries == result


def test_none_not_in_range():
    assert (None in KTDateRange('2026-01-01', '2026-01-10')) is False


@pytest.mark.parametrize(
    'ranges, result',
    [
        pytest.param(
            [('2026-01-10', '2026-01-19'), ('2026-02-01', '2026-02-10')],
            [('2026-01-01', '2026-01-10'), ('2026-01-20', '2026-02-01'), ('2026-02-11', '2026-03-01')],
            id='leading-middle-trailing',
        ),
        pytest.param([('2025-12-01', '2026-12-31')], [], id='fully-covered'),
        pytest.param([], [('2026-01-01', '2026-03-01')], id='no-ranges'),
        pytest.param([('2026-01-15', None)], [('2026-01-01', '2026-01-15')], id='unbounded-upper'),
        pytest.param([(None, '2026-01-15')], [('2026-01-16', '2026-03-01')], id='unbounded-lower'),
        pytest.param(
            [('2026-01-01', '2026-01-31'), ('2026-02-01', '2026-02-28')],
            [],
            id='adjacent-no-false-gap',
        ),
        pytest.param(
            [('2025-12-15', '2026-01-05'), ('2026-02-20', '2026-03-15')],
            [('2026-01-06', '2026-02-20')],
            id='clipped-to-window',
        ),
        pytest.param(
            [('2026-02-01', '2026-02-10'), ('2026-01-10', '2026-01-19')],
            [('2026-01-01', '2026-01-10'), ('2026-01-20', '2026-02-01'), ('2026-02-11', '2026-03-01')],
            id='unsorted-input',
        ),
        pytest.param(['2026-01-15'], [('2026-01-01', '2026-01-15'), ('2026-01-16', '2026-03-01')], id='single-day'),
    ],
)
def test_gaps(ranges, result):
    ranges = [KTDateRange.from_start_end(*r) if isinstance(r, tuple) else r for r in ranges]
    gaps = KTDateRange.gaps(ranges, '2026-01-01', '2026-02-28')
    assert [g.boundaries for g in gaps] == [(dt(lo), dt(hi)) for lo, hi in result]


def test_gaps_empty_ranges_ignored():
    gaps = KTDateRange.gaps([KTDateRange(empty=True)], '2026-01-01', '2026-01-31')
    assert [g.boundaries for g in gaps] == [(dt('2026-01-01'), dt('2026-02-01'))]


def test_gaps_calendar_binds_results():
    cal = KTCalendar(country_code='IT')
    (gap,) = KTDateRange.gaps([], '2026-01-01', '2026-01-31', ktcalendar=cal)
    assert gap.ktcalendar is cal


@pytest.mark.parametrize(
    'period, boundaries',
    [
        pytest.param(('2026-01-01', '2026-01-10'), (dt('2026-01-01'), dt('2026-01-09')), id='bounded'),
        pytest.param((None, '2026-01-10'), (datetime.date.min, dt('2026-01-09')), id='unbounded-lower'),
        pytest.param(('2026-01-01', None), (dt('2026-01-01'), datetime.date.max), id='unbounded-upper'),
        pytest.param((None, None), (datetime.date.min, datetime.date.max), id='unbounded-both'),
    ],
)
def test_as_dates(period, boundaries):
    assert KTDateRange(*period).as_dates() == boundaries


def test_as_dates_empty():
    dr = KTDateRange(empty=True)
    assert dr.isempty
    assert dr.boundaries == (None, None)
    with pytest.raises(ValueError, match='Unable to extract dates: date range is empty'):
        dr.as_dates()


def test_calendar_binds_produced_days():
    dr = KTDateRange('2025-06-01', '2025-06-04', cal_country_code='IT')
    assert dr.ktcalendar.country_calendar_code == 'IT'
    days = list(dr)
    assert all(day.ktcalendar is dr.ktcalendar for day in days)
    assert days[1].is_holiday is True, 'Should be Bank Hol in Italy'


def test_calendar_precedence():
    cal = KTCalendar(country_code='IT')
    assert KTDateRange('2025-06-01', '2025-06-04', ktcalendar=cal).ktcalendar is cal
    assert KTDateRange('2025-06-01', '2025-06-04', ktcalendar=cal, cal_country_code='GB-ENG').ktcalendar is cal
    default = KTDateRange('2025-06-01', '2025-06-04').ktcalendar
    assert default.country_calendar_code == KTCalendar.get_default_country_code()


def test_calendar_copy_inheritance():
    cal = KTCalendar(country_code='IT')
    dr = KTDateRange('2025-06-01', '2025-06-04', ktcalendar=cal)
    assert KTDateRange(dr).ktcalendar is cal
    other = KTCalendar(country_code='GB-ENG')
    assert KTDateRange(dr, ktcalendar=other).ktcalendar is other
    assert KTDateRange(dr, cal_country_code='GB-ENG').ktcalendar.country_calendar_code == 'GB-ENG'


def test_calendar_from_start_end():
    cal = KTCalendar(country_code='IT')
    dr = KTDateRange.from_start_end('2025-06-01', '2025-06-02', ktcalendar=cal)
    assert dr.ktcalendar is cal
    assert all(day.ktcalendar is cal for day in dr)


def test_calendar_empty_range():
    dr = KTDateRange(empty=True, cal_country_code='IT')
    assert dr.ktcalendar.country_calendar_code == 'IT'


def test_extra_kwargs_become_attributes():
    dr = KTDateRange('2025-06-01', '2025-06-04', name='sprint-1')
    assert dr.name == 'sprint-1'


def test_equality_ignores_calendar_and_attributes():
    assert KTDateRange('2025-06-01', '2025-06-04', cal_country_code='IT') == KTDateRange(
        '2025-06-01', '2025-06-04', cal_country_code='GB-ENG', name='sprint-1'
    )


def test_pickle_preserves_calendar_and_attributes():
    dr = KTDateRange('2025-06-01', '2025-06-04', cal_country_code='IT', name='sprint-1')
    roundtripped = pickle.loads(pickle.dumps(dr))
    assert roundtripped == dr
    assert roundtripped.ktcalendar.country_calendar_code == 'IT'
    assert roundtripped.name == 'sprint-1'
    assert list(roundtripped)[1].is_holiday is True, 'Should be Bank Hol in Italy'


def test_parsing_consistency_with_ktday():
    with pytest.raises(ValueError, match="Invalid date: 'dummy'"):
        KTDay('dummy')
    with pytest.raises(ValueError, match="Invalid date: 'dummy'"):
        KTDateRange('dummy', '2025-06-04')
    # documented deviation: None means unbounded, not today as in KTDay(None)
    assert KTDateRange(None, None).boundaries == (None, None)


@pytest.mark.parametrize(
    'other',
    [
        pytest.param('2026-02-01', id='str'),
        pytest.param(dt('2026-02-01'), id='date'),
        pytest.param(KTDay('2026-02-01'), id='ktday'),
        pytest.param(DateRange(dt('2026-02-01'), dt('2026-02-10')), id='daterange'),
        pytest.param(('2026-02-01', '2026-02-10'), id='tuple'),
    ],
)
def test_other_types(other):
    """The comparison methods accept plain DateRanges, tuples and KTDay-compatible values."""
    assert KTDateRange('2026-01-01', '2026-02-01').precedes(other) is True
    assert KTDateRange('2026-01-01', '2026-01-20').fully_lt(other) is True
    assert KTDateRange('2026-01-01', '2026-02-05').fully_lt(other) is False
