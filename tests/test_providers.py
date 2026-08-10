import sys
import types

import pytest

from ktcalendars.days import KTDay
from ktcalendars.providers import (
    AbstractExtraHolidayProvider,
    NoExtraHolidayProvider,
    extra_holiday_provider,
    load_extra_holiday_provider,
)


class ChristmasEveClosure(AbstractExtraHolidayProvider):
    @classmethod
    def is_extra_holiday(cls, ktd: KTDay, country_calendar_code: str) -> bool:
        return (ktd.month, ktd.day) == (12, 24)


@pytest.fixture
def fake_provider_module(monkeypatch):
    module = types.ModuleType('fake_provider_module')
    module.ChristmasEveClosure = ChristmasEveClosure  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, 'fake_provider_module', module)
    return module


class TestExtraHolidayProvider:
    def test_abstract_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            AbstractExtraHolidayProvider()  # type: ignore[abstract]

    def test_default_provider_never_flags_extra_holidays(self):
        assert NoExtraHolidayProvider().is_extra_holiday(KTDay('2025-12-24'), 'GB-ENG') is False

    def test_module_level_provider_is_default(self):
        assert isinstance(extra_holiday_provider, NoExtraHolidayProvider)


class TestLoadExtraHolidayProvider:
    def test_defaults_when_env_var_unset(self, monkeypatch):
        monkeypatch.delenv('EXTRA_HOLIDAY_PROVIDER', raising=False)
        assert isinstance(load_extra_holiday_provider(), NoExtraHolidayProvider)

    def test_loads_provider_from_env_var(self, monkeypatch, fake_provider_module):
        monkeypatch.setenv('EXTRA_HOLIDAY_PROVIDER', 'fake_provider_module.ChristmasEveClosure')
        provider = load_extra_holiday_provider()
        assert isinstance(provider, ChristmasEveClosure)
        assert provider.is_extra_holiday(KTDay('2025-12-24'), 'GB-ENG') is True
        assert provider.is_extra_holiday(KTDay('2025-12-23'), 'GB-ENG') is False

    def test_unqualified_name_raises(self, monkeypatch):
        monkeypatch.setenv('EXTRA_HOLIDAY_PROVIDER', 'NotQualified')
        with pytest.raises(ValueError, match='fully qualified name'):
            load_extra_holiday_provider()

    def test_non_subclass_raises(self, monkeypatch):
        monkeypatch.setenv('EXTRA_HOLIDAY_PROVIDER', 'datetime.date')
        with pytest.raises(TypeError, match='not a subclass of AbstractExtraHolidayProvider'):
            load_extra_holiday_provider()

    def test_unknown_module_raises(self, monkeypatch):
        monkeypatch.setenv('EXTRA_HOLIDAY_PROVIDER', 'no.such.module.Provider')
        with pytest.raises(ModuleNotFoundError):
            load_extra_holiday_provider()
