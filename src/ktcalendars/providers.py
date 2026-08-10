"""Pluggable providers for extending holiday detection with custom sources."""

from __future__ import annotations

import abc
import importlib
import os
import typing

if typing.TYPE_CHECKING:
    from ktcalendars.days import KTDay

__all__ = ["AbstractExtraHolidayProvider", "NoExtraHolidayProvider", "extra_holiday_provider"]


class AbstractExtraHolidayProvider(abc.ABC):
    """Abstract base class for extra holiday providers.

    Subclass this to provide your own way of detecting extra holidays
    (e.g. company closures) and set the ``EXTRA_HOLIDAY_PROVIDER``
    environment variable to the fully qualified name of your subclass.
    """

    @classmethod
    @abc.abstractmethod
    def is_extra_holiday(cls, ktd: KTDay, country_calendar_code: str) -> bool:
        """Return True if the given KTDay is recorded as extra holiday for the provided country calendar code."""


class NoExtraHolidayProvider(AbstractExtraHolidayProvider):
    """Default extra holiday provider: no day is ever an extra holiday."""

    @classmethod
    def is_extra_holiday(cls, ktd: KTDay, country_calendar_code: str) -> bool:
        """Return True if the given KTDay is recorded as extra holiday for the provided country calendar code."""
        return False


def load_extra_holiday_provider() -> AbstractExtraHolidayProvider:
    """Instantiate the provider named by the ``EXTRA_HOLIDAY_PROVIDER`` environment variable.

    The variable must hold the fully qualified name of an
    `AbstractExtraHolidayProvider` subclass (e.g. ``"mypackage.mymodule.CompanyClosures"``).
    When unset, the default `NoExtraHolidayProvider` is used.
    """
    fqn = os.environ.get("EXTRA_HOLIDAY_PROVIDER")
    if not fqn:
        return NoExtraHolidayProvider()
    module_name, _, class_name = fqn.rpartition(".")
    if not module_name:
        raise ValueError(f"EXTRA_HOLIDAY_PROVIDER must be a fully qualified name. Got {fqn!r}")
    provider_class = getattr(importlib.import_module(module_name), class_name)
    if not (isinstance(provider_class, type) and issubclass(provider_class, AbstractExtraHolidayProvider)):
        raise TypeError(f"{fqn} is not a subclass of AbstractExtraHolidayProvider")
    return provider_class()


extra_holiday_provider = load_extra_holiday_provider()
