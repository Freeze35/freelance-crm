from django.conf import settings

def test_essential_apps_installed():
    """We check that all key CRM applications are in the list"""
    essential_apps = ['clients', 'projects', 'tasks', 'invoices']
    for app in essential_apps:
        assert app in settings.INSTALLED_APPS

def test_timezone_is_moscow():
    """Checking the correct time zone (important for notifications)"""
    assert settings.TIME_ZONE == 'Europe/Moscow'
    assert settings.LANGUAGE_CODE == 'ru-ru'

def test_database_is_sqlite_in_tests():
    """Checking that a fast in-memory database is used for tests"""
    db_config = settings.DATABASES['default']
    assert db_config['ENGINE'] == 'django.db.backends.sqlite3'
    assert 'memory' in db_config['NAME']


def test_celery_schedule_exists():
    """Checking that notification tasks are registered with Beat"""
    schedule = settings.CELERY_BEAT_SCHEDULE
    assert 'send_notifications_9am' in schedule
    assert 'send_notifications_6pm' in schedule

    assert schedule['send_notifications_9am']['task'] == 'tasks.tasks.send_telegram_notifications'

def test_telegram_settings_load():
    """Checking for the presence of variables for the bot (even if they are empty)"""
    # We expect a string, not None
    assert isinstance(settings.TELEGRAM_BOT_TOKEN, str)
    assert isinstance(settings.TELEGRAM_CHAT_ID, str)