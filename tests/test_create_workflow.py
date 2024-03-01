from unittest import TestCase
from assertpy import assert_that
from fastapi.testclient import TestClient
from sqlmodel import select
from microservice.db.engine import get_test_session, get_session

from microservice.api import app
from microservice.db.models import Workflow, Component


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

    def test_worflow_without_settings(self):
        workflow_wo_settings = {
            "name": "workflow_wo_settings",
            "components": [
                {"type": "export"},
                {"type": "crop"},
                {"type": "shadow"},
                {"type": "import"}
            ]
        }

        response = self.client.post(
            "/workflow/", json=workflow_wo_settings
        )

        assert_that(response.status_code).is_equal_to(200)
        workflow_wo_settings_id = response.json()
        assert_that(workflow_wo_settings_id).is_instance_of(str)

        with next(get_test_session()) as session:
            # assert workflow result
            wfwo = session.get(Workflow, workflow_wo_settings_id)
            assert_that(str(wfwo.id)).is_equal_to(workflow_wo_settings_id)
            assert_that(wfwo.name).is_equal_to(workflow_wo_settings["name"])
            # assert component result
            statement = select(Component).where(Component.workflow_id == str(wfwo.id)).order_by(Component.order.asc())
            results = session.exec(statement)
            components = results.all()
            assert_that(str(components[0].component_type)).is_equal_to(workflow_wo_settings["components"][0]["type"])
            assert_that(str(components[1].component_type)).is_equal_to(workflow_wo_settings["components"][1]["type"])
            assert_that(str(components[2].component_type)).is_equal_to(workflow_wo_settings["components"][2]["type"])
            assert_that(str(components[3].component_type)).is_equal_to(workflow_wo_settings["components"][3]["type"])
            assert_that(components[0].order).is_equal_to(0)
            assert_that(components[1].order).is_equal_to(1)
            assert_that(components[2].order).is_equal_to(2)
            assert_that(components[3].order).is_equal_to(3)

    def test_worflow_with_settings(self):
        workflow_settings = {
            "name": "workflow_settings",
            "components": [
                {"type": "import", "settings": {"format": "PNG", "downscale": True}},
                {"type": "shadow", "settings": {"intensity": 0.1}}
            ]
        }

        response = self.client.post(
            "/workflow/", json=workflow_settings
        )

        assert_that(response.status_code).is_equal_to(200)
        workflow_settings_id = response.json()
        assert_that(workflow_settings_id).is_instance_of(str)

        with next(get_test_session()) as session:
            # assert workflow result
            wfs = session.get(Workflow, workflow_settings_id)
            assert_that(str(wfs.id)).is_equal_to(workflow_settings_id)
            assert_that(wfs.name).is_equal_to(workflow_settings["name"])
            # assert component result
            statement = select(Component).where(Component.workflow_id == str(wfs.id)).order_by(Component.order.asc())
            results = session.exec(statement)
            components = results.all()
            assert_that(str(components[0].component_type)).is_equal_to(workflow_settings["components"][0]["type"])
            assert_that(str(components[1].component_type)).is_equal_to(workflow_settings["components"][1]["type"])
            assert_that(components[0].component_settings).is_equal_to(workflow_settings["components"][0]["settings"])
            assert_that(components[1].component_settings).is_equal_to(workflow_settings["components"][1]["settings"])
            assert_that(components[0].order).is_equal_to(0)
            assert_that(components[1].order).is_equal_to(1)
