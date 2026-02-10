import pytest
from django.conf import settings
from typing import List, Dict, Any, Final


@pytest.mark.django_db
class TestProjectSettings:
    """Tests to ensure the Django environment and settings are configured correctly"""

    def test_essential_apps_installed(self) -> None:
        """Check that all key CRM applications are present in INSTALLED_APPS"""
        essential_apps: Final[List[str]] = ['clients', 'projects', 'tasks', 'invoices']
        installed_apps: List[str] = list(settings.INSTALLED_APPS)

        for app in essential_apps:
            assert app in installed_apps

    def test_timezone_is_moscow(self) -> None:
        """Verify the correct time zone and language code for the region"""
        assert settings.TIME_ZONE == 'Europe/Moscow'
        assert settings.LANGUAGE_CODE == 'ru-ru'

    def test_database_is_sqlite_in_tests(self) -> None:
        """Verify that a fast in-memory SQLite database is used for testing"""
        db_config: Dict[str, Any] = settings.DATABASES['default']

        assert db_config['ENGINE'] == 'django.db.backends.sqlite3'
        assert 'memory' in db_config['NAME']

    def test_celery_schedule_exists(self) -> None:
        """Verify that notification tasks are registered within Celery Beat schedule"""
        schedule: Dict[str, Any] = getattr(settings, 'CELERY_BEAT_SCHEDULE', {})

        assert 'send_notifications_9am' in schedule
        assert 'send_notifications_6pm' in schedule

        task_name: str = schedule['send_notifications_9am']['task']
        assert task_name == 'tasks.tasks.send_telegram_notifications'

    def test_telegram_settings_load(self) -> None:
        """Ensure Telegram bot configuration variables are present and are strings"""
        bot_token: Any = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
        chat_id: Any = getattr(settings, 'TELEGRAM_CHAT_ID', None)

        assert isinstance(bot_token, str)
        assert isinstance(chat_id, str)