from unittest import TestCase
from assertpy import assert_that
from fastapi.testclient import TestClient
from microservice.db.engine import get_test_session, get_session

from microservice.api import app
from microservice.db.models import Workflow


class TestAPI(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        app.dependency_overrides[get_session] = get_test_session
        cls.client = TestClient(app)

    @classmethod
    def tearDown(cls) -> None:
        app.dependency_overrides.clear()

    def test_should_create_workflow_with_name(self):
        given_workflow = {"name": "test"}

        response = self.client.post(
            "/workflow/", json=given_workflow
        )

        assert_that(response.status_code).is_equal_to(200)
        workflow_id = response.json()
        assert_that(workflow_id).is_instance_of(str)

        # without a GET endpoint, we look directly in the db
        with next(get_test_session()) as session:
            wf = session.get(Workflow, workflow_id)
            assert_that(str(wf.id)).is_equal_to(workflow_id)
            assert_that(wf.name).is_equal_to(given_workflow["name"])

    # TODO: test components support and validation
