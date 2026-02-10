import pytest
from projects.models import Project
from clients.models import Client
from django.utils import timezone
from datetime import timedelta
from typing import Final


@pytest.mark.django_db
class TestProjectModel:
    """Tests for Project model logic and database integrity"""

    def test_project_creation(self, project: Project) -> None:
        """Verify successful creation and string representation of a project"""
        assert str(project) == f"{project.name} ({project.client})"

        valid_statuses: Final[list[str]] = ['new', 'in_progress', 'completed', 'canceled']
        assert project.status in valid_statuses

    def test_project_budget_precision(self, project: Project) -> None:
        """Verify that decimal precision is maintained for the budget field"""
        expected_budget: Final[float] = 12345.67
        project.budget = expected_budget
        project.save()

        assert float(project.budget) == expected_budget

    def test_client_cascade_deletion(self, project: Project) -> None:
        """Verify that projects are deleted when their associated client is removed"""
        associated_client: Client = project.client
        project_id: int = project.pk

        associated_client.delete()

        assert Project.objects.filter(id=project_id).count() == 0