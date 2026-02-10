import pytest
from django.utils import timezone
from datetime import timedelta
from projects.models import Project


@pytest.mark.django_db
class TestProjectModel:

    def test_project_str_representation(self, project):
        expected_name = f"{project.name} ({project.client})"
        assert str(project) == expected_name

    def test_cascade_delete_client(self, project):
        """Checking that deleting a client also deletes its projects"""
        client = project.client
        client.delete()
        # We check that the project that was linked to this client has disappeared
        assert Project.objects.filter(id=project.id).count() == 0