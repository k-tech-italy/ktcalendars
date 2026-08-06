from __future__ import annotations


class ExtraHolidayProvider:
    """Default extra holiday provider.

    Extend this class to provide your own way of detecting extra holidays.
    """

    @classmethod
    def is_extra_holiday(cls, ktd: KTDay, country_calendar_code: str) -> bool:
        """Return True if the given KTDay is recorded as extra holiday for the provided country calendar code."""
        return False


extra_holiday_provider = ExtraHolidayProvider()
