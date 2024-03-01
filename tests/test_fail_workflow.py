from unittest import TestCase
from assertpy import assert_that
from fastapi.testclient import TestClient
from sqlmodel import select
from microservice.db.engine import get_test_session, get_session

from microservice.api import app
from microservice.db.models import Workflow, Component


class TestFailAPI(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        app.dependency_overrides[get_session] = get_test_session
        cls.client = TestClient(app)

    @classmethod
    def tearDown(cls) -> None:
        app.dependency_overrides.clear()

    def test_invalid_workflow_parameter(self):
        workflow_invalid_parameter = {
            "name": "workflow_invalid_parameter",
            "unexisting_parameter": "test"
        }

        response = self.client.post(
            "/workflow/", json=workflow_invalid_parameter
        )

        assert_that(response.status_code).is_equal_to(422)
        assert_that(response.json()["detail"][0]["msg"]).is_equal_to("Extra inputs are not permitted")
        assert_that(response.json()["detail"][0]["loc"]).is_equal_to(['body', 'unexisting_parameter'])

    def test_invalid_component_parameter(self):
        component_invalid_parameter = {
            "name": "component_invalid_parameter",
            "components": [
                {"unexisting_type": "type"}
            ]
        }

        response = self.client.post(
            "/workflow/", json=component_invalid_parameter
        )

        assert_that(response.status_code).is_equal_to(422)
        assert_that(response.json()["detail"][0]["msg"]).is_equal_to("Field required")
        assert_that(response.json()["detail"][0]["loc"]).is_equal_to(['body', 'components', 0, 'type'])

    def test_invalid_type(self):
        component_invalid_type = {
            "name": "component_invalid_parameter",
            "components": [
                {"type": "unexisting"}
            ]
        }

        response = self.client.post(
            "/workflow/", json=component_invalid_type
        )

        assert_that(response.status_code).is_equal_to(422)
        assert_that(response.json()["detail"][0]["msg"]).is_equal_to("Value error, Invalid value of type: unexisting")

    def test_duplicate_type(self):
        component_duplicate_type = {
            "name": "component_duplicate_type",
            "components": [
                {"type": "import", "settings": {"format": "PNG", "downscale": True}},
                {"type": "import", "settings": {"intensity": 0.1}}
            ]
        }

        response = self.client.post(
            "/workflow/", json=component_duplicate_type
        )

        assert_that(response.status_code).is_equal_to(422)
        assert_that(response.json()["detail"][0]["msg"]).is_equal_to("Value error, There should be only one occurence of each type: ['import', 'import']")

    def test_import_first(self):
        component_import_second = {
            "name": "component_import_second",
            "components": [
                {"type": "shadow", "settings": {"intensity": 0.1}},
                {"type": "import", "settings": {"format": "PNG", "downscale": True}}
            ]
        }

        response = self.client.post(
            "/workflow/", json=component_import_second
        )

        assert_that(response.status_code).is_equal_to(422)
        assert_that(response.json()["detail"][0]["msg"]).is_equal_to("Value error, import should be first in the list of settings")

    def test_export_last(self):
        component_export_first = {
            "name": "component_export_first",
            "components": [
                {"type": "export", "settings": {"format": "PNG", "downscale": True}},
                {"type": "shadow", "settings": {"intensity": 0.1}}
            ]
        }

        response = self.client.post(
            "/workflow/", json=component_export_first
        )

        assert_that(response.status_code).is_equal_to(422)
        assert_that(response.json()["detail"][0]["msg"]).is_equal_to("Value error, export should be last in the list of settings")

    def test_settings_for_few(self):
        settings_for_few = {
            "name": "settings_for_few",
            "components": [
                {"type": "import", "settings": {"format": "PNG", "downscale": True}},
                {"type": "shadow", "settings": {"intensity": 0.1}},
                {"type": "crop"},
                {"type": "export", "settings": {"format": "JPG"}}
            ]
        }

        response = self.client.post(
            "/workflow/", json=settings_for_few
        )

        assert_that(response.status_code).is_equal_to(422)
        assert_that(response.json()["detail"][0]["msg"]).is_equal_to("Value error, All component should either contain the settings fields or none shall contain it")
