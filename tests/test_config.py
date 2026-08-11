import datetime
import sys
import types

import pytest

from ktcalendars.config import (
    AbstractConfiguration,
    DefaultConfiguration,
    get_configuration,
    load_configuration,
    reset_configuration,
)
from ktcalendars.days import KTDay


class CompanyClosures(AbstractConfiguration):
    closures_by_country = {
        'GB-ENG': {
            datetime.date(2025, 12, 24): 'Christmas Eve closure',
            datetime.date(2025, 12, 31): "New Year's Eve closure",
            datetime.date(2026, 12, 24): 'Christmas Eve closure',
        },
    }

    def get_holiday_overrides(self, country_calendar_code, from_date=None, to_date=None):
        overrides = self.closures_by_country.get(country_calendar_code, {})
        return {
            day: name
            for day, name in overrides.items()
            if (from_date is None or day >= from_date) and (to_date is None or day <= to_date)
        }


@pytest.fixture
def fake_config_module(monkeypatch):
    module = types.ModuleType('fake_config_module')
    module.CompanyClosures = CompanyClosures  # type: ignore[attr-defined]
    monkeypatch.setitem(sys.modules, 'fake_config_module', module)
    return module


@pytest.fixture
def company_closures_config(monkeypatch, fake_config_module):
    monkeypatch.setenv('KTCALENDAR_CONFIG', 'fake_config_module.CompanyClosures')
    reset_configuration()
    return get_configuration()


class TestAbstractConfiguration:
    def test_abstract_class_cannot_be_instantiated(self):
        with pytest.raises(TypeError):
            AbstractConfiguration()  # type: ignore[abstract]

    def test_default_country_code_from_ktcalendar_country(self, monkeypatch):
        monkeypatch.setenv('KTCALENDAR_COUNTRY', 'IT-RM')
        monkeypatch.setenv('DEFAULT_HOLIDAYS_CALENDAR', 'US-CA')
        assert DefaultConfiguration().get_default_country_code() == 'IT-RM'

    def test_default_country_code_from_legacy_env_var_warns(self, monkeypatch):
        monkeypatch.delenv('KTCALENDAR_COUNTRY', raising=False)
        monkeypatch.setenv('DEFAULT_HOLIDAYS_CALENDAR', 'US-CA')
        with pytest.warns(DeprecationWarning, match='DEFAULT_HOLIDAYS_CALENDAR.*deprecated'):
            assert DefaultConfiguration().get_default_country_code() == 'US-CA'

    def test_default_country_code_fallback(self, monkeypatch):
        monkeypatch.delenv('KTCALENDAR_COUNTRY', raising=False)
        monkeypatch.delenv('DEFAULT_HOLIDAYS_CALENDAR', raising=False)
        assert DefaultConfiguration().get_default_country_code() == 'GB-ENG'


class TestDefaultConfiguration:
    def test_no_holiday_overrides(self):
        assert DefaultConfiguration().get_holiday_overrides('GB-ENG') == {}


class TestLoadConfiguration:
    def test_defaults_when_env_var_unset(self, monkeypatch):
        monkeypatch.delenv('KTCALENDAR_CONFIG', raising=False)
        assert isinstance(load_configuration(), DefaultConfiguration)

    def test_loads_configuration_from_env_var(self, monkeypatch, fake_config_module):
        monkeypatch.setenv('KTCALENDAR_CONFIG', 'fake_config_module.CompanyClosures')
        assert isinstance(load_configuration(), CompanyClosures)

    def test_unqualified_name_raises(self, monkeypatch):
        monkeypatch.setenv('KTCALENDAR_CONFIG', 'NotQualified')
        with pytest.raises(ValueError, match='fully qualified name'):
            load_configuration()

    def test_non_subclass_raises(self, monkeypatch):
        monkeypatch.setenv('KTCALENDAR_CONFIG', 'datetime.date')
        with pytest.raises(TypeError, match='not a subclass of AbstractConfiguration'):
            load_configuration()

    def test_unknown_module_raises(self, monkeypatch):
        monkeypatch.setenv('KTCALENDAR_CONFIG', 'no.such.module.Configuration')
        with pytest.raises(ModuleNotFoundError):
            load_configuration()


class TestGetConfiguration:
    def test_lazily_loads_and_caches(self, monkeypatch):
        monkeypatch.delenv('KTCALENDAR_CONFIG', raising=False)
        configuration = get_configuration()
        assert isinstance(configuration, DefaultConfiguration)
        assert get_configuration() is configuration

    def test_reset_reloads(self, monkeypatch, fake_config_module):
        assert isinstance(get_configuration(), DefaultConfiguration)
        monkeypatch.setenv('KTCALENDAR_CONFIG', 'fake_config_module.CompanyClosures')
        assert isinstance(get_configuration(), DefaultConfiguration), 'Still cached'
        reset_configuration()
        assert isinstance(get_configuration(), CompanyClosures)


class TestHolidayOverrides:
    def test_no_range_returns_all(self, company_closures_config):
        assert len(company_closures_config.get_holiday_overrides('GB-ENG')) == 3

    def test_from_date_only(self, company_closures_config):
        overrides = company_closures_config.get_holiday_overrides('GB-ENG', from_date=datetime.date(2025, 12, 25))
        assert list(overrides) == [datetime.date(2025, 12, 31), datetime.date(2026, 12, 24)]

    def test_to_date_only(self, company_closures_config):
        overrides = company_closures_config.get_holiday_overrides('GB-ENG', to_date=datetime.date(2025, 12, 31))
        assert list(overrides) == [datetime.date(2025, 12, 24), datetime.date(2025, 12, 31)]

    def test_both_bounds_inclusive(self, company_closures_config):
        overrides = company_closures_config.get_holiday_overrides(
            'GB-ENG', from_date=datetime.date(2025, 12, 24), to_date=datetime.date(2025, 12, 31)
        )
        assert list(overrides) == [datetime.date(2025, 12, 24), datetime.date(2025, 12, 31)]

    def test_unknown_country_code_returns_empty_mapping(self, company_closures_config):
        assert company_closures_config.get_holiday_overrides('IT') == {}

    def test_overrides_are_reflected_by_ktday(self, company_closures_config):
        assert KTDay('2025-12-24').is_extra_holiday() is True
        assert KTDay('2025-12-24').is_holiday() is True
        assert KTDay('2025-12-24').is_non_working_day() is True
        assert KTDay('2025-12-23').is_extra_holiday() is False
        assert KTDay('2025-12-23').is_holiday() is False
        assert KTDay('2025-12-24').is_extra_holiday('IT') is False, 'No overrides for Italy'
