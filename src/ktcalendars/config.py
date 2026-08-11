"""Pluggable configuration class centralising ktcalendars settings."""

from __future__ import annotations

import abc
import functools
import importlib
import os
import typing
import warnings

if typing.TYPE_CHECKING:
    import datetime

__all__ = [
    "AbstractConfiguration",
    "DefaultConfiguration",
    "get_configuration",
    "load_configuration",
    "reset_configuration",
]


class AbstractConfiguration(abc.ABC):
    """Abstract base class for ktcalendars configuration classes.

    Subclass this to provide holiday overrides and the default country
    calendar code, and set the ``KTCALENDAR_CONFIG`` environment variable
    to the fully qualified name of your subclass.
    """

    @abc.abstractmethod
    def get_holiday_overrides(
        self,
        country_calendar_code: str,
        from_date: datetime.date | None = None,
        to_date: datetime.date | None = None,
    ) -> dict[datetime.date, str]:
        """Return the holiday overrides for a country calendar code as a date → name mapping.

        Overrides are additive: they are merged on top of the holidays
        provided by the `holidays` package for the country calendar code.
        `from_date` and `to_date` restrict the result to an inclusive range
        and are each independently optional. An unknown country calendar
        code returns an empty mapping.
        """

    def get_default_country_code(self) -> str:
        """Return the default country calendar code (e.g. ``"GB-ENG"``).

        Defaults to the ``KTCALENDAR_COUNTRY`` environment variable, then the
        deprecated ``DEFAULT_HOLIDAYS_CALENDAR`` one, falling back to
        ``"GB-ENG"``. Override this method to customise.
        """
        code = os.environ.get("KTCALENDAR_COUNTRY")
        if code:
            return code
        legacy = os.environ.get("DEFAULT_HOLIDAYS_CALENDAR")
        if legacy:
            warnings.warn(
                "The DEFAULT_HOLIDAYS_CALENDAR environment variable is deprecated; use KTCALENDAR_COUNTRY instead",
                DeprecationWarning,
                stacklevel=2,
            )
            return legacy
        return "GB-ENG"


class DefaultConfiguration(AbstractConfiguration):
    """Default configuration: no holiday overrides, environment-driven country code."""

    def get_holiday_overrides(
        self,
        country_calendar_code: str,
        from_date: datetime.date | None = None,
        to_date: datetime.date | None = None,
    ) -> dict[datetime.date, str]:
        """Return no holiday overrides."""
        return {}


def load_configuration() -> AbstractConfiguration:
    """Instantiate the configuration named by the ``KTCALENDAR_CONFIG`` environment variable.

    The variable must hold the fully qualified name of an
    `AbstractConfiguration` subclass (e.g. ``"mypackage.config.MyConfiguration"``).
    When unset, the default `DefaultConfiguration` is used.
    """
    fqn = os.environ.get("KTCALENDAR_CONFIG")
    if not fqn:
        return DefaultConfiguration()
    module_name, _, class_name = fqn.rpartition(".")
    if not module_name:
        raise ValueError(f"KTCALENDAR_CONFIG must be a fully qualified name. Got {fqn!r}")
    configuration_class = getattr(importlib.import_module(module_name), class_name)
    if not (isinstance(configuration_class, type) and issubclass(configuration_class, AbstractConfiguration)):
        raise TypeError(f"{fqn} is not a subclass of AbstractConfiguration")
    return configuration_class()


@functools.cache
def get_configuration() -> AbstractConfiguration:
    """Return the configuration singleton, loading it lazily on first use."""
    return load_configuration()


def reset_configuration() -> None:
    """Clear the cached configuration so the next use reloads it (mainly for tests)."""
    get_configuration.cache_clear()
