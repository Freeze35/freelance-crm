import pytest
from tasks.forms import TaskForm
from typing import Dict, Any

@pytest.mark.django_db
class TestTaskForm:

    def test_task_form_valid_data(self) -> None:
        """Verify the form is valid when all required fields are correctly filled"""
        form_data: Dict[str, Any] = {
            'title': 'Написать документацию',
            'description': 'Описать все эндпоинты API',
            'status': 'todo',
            'deadline': '2026-12-31'
        }
        form: TaskForm = TaskForm(data=form_data)
        assert form.is_valid(), f"Form errors: {form.errors}"

    def test_task_form_invalid_data(self) -> None:
        """Verify the form is invalid when the title field is empty"""
        form: TaskForm = TaskForm(data={'title': ''})
        assert not form.is_valid()
        assert 'title' in form.errors