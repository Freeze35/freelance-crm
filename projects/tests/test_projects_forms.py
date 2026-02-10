import pytest
from projects.models import Project
from django.utils import timezone
from datetime import timedelta


@pytest.mark.django_db
class TestProjectModel:

    def test_project_creation(self, project):  # Используем 'project'
        """Checking successful creation and __str__"""
        # project.client is already created automatically by the fixture
        assert str(project) == f"{project.name} ({project.client})"
        assert project.status in ['new', 'in_progress', 'done', 'canceled']

    def test_project_budget_precision(self, project):
        """Budget Accuracy Check"""
        project.budget = 12345.67
        project.save()
        assert project.budget == 12345.67

    def test_client_cascade_deletion(self, project):
        """Checking cascading deletion"""
        client = project.client
        client.delete()
        # If the client is deleted, the project should also disappear (on_delete=models.CASCADE)
        assert Project.objects.filter(id=project.id).count() == 0