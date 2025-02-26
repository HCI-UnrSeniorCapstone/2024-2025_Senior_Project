import pytest
from unittest.mock import patch
import json

from app import create_app
from app.utility.db_connection import get_db_connection


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


def test_get_study_data_code(client):
    response = client.get("/get_study_data/1")
    assert response.status_code == 200
