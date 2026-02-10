import pytest
from tasks.forms import TaskForm
from tasks.models import Task


@pytest.mark.django_db
class TestTaskForm:

    def test_task_form_valid_data(self):
        """Проверка формы с корректными данными"""
        form_data = {
            'title': 'Написать документацию',
            'description': 'Описать все эндпоинты API',
            'status': 'todo',
            'deadline': '2026-12-31'
        }
        form = TaskForm(data=form_data)
        assert form.is_valid(), f"Ошибки формы: {form.errors}"

    def test_task_form_invalid_data(self):
        """Проверка обязательных полей (title обычно обязателен)"""
        form = TaskForm(data={'title': ''})
        assert not form.is_valid()
        assert 'title' in form.errors