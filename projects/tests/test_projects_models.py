import pytest
from projects.models import Project
from clients.models import Client


@pytest.mark.django_db
class TestProjectModel:

    def test_project_str_representation(self, project: Project) -> None:
        """Verify the project string representation format"""
        expected_name: str = f"{project.name} ({project.client})"
        assert str(project) == expected_name

    def test_cascade_delete_client(self, project: Project) -> None:
        """Verify that deleting a client also deletes its associated projects"""
        client: Client = project.client
        project_pk: int = project.pk

        client.delete()

        assert Project.objects.filter(pk=project_pk).count() == 0