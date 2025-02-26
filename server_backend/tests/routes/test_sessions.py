import pytest
from unittest.mock import patch
import json

from app import create_app


@pytest.fixture
def app():
    # Create and configure the app for testing
    app = create_app(testing=True)
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    # Create a test client for the app
    return app.test_client()


def test_get_all_session_data_instance_from_participant_zip_fail(client):
    response = client.get("/get_all_session_data_instance_from_participant_zip/64")
    assert response.status_code == 500
    assert response.data == "hi"
