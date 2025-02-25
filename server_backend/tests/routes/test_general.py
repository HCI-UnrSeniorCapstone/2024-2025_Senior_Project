import pytest
from unittest.mock import patch
import json

# from ...app import create_app
from app import create_app

# from server_backend.app.routes import *


@pytest.fixture
def app():
    # Create and configure the app for testing
    app = create_app()
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app):
    # Create a test client for the app
    return app.test_client()


def test_ping(client):
    # Send a GET request to the /ping endpoint
    response = client.get("/ping")

    # Assert the response status code
    assert response.status_code == 200

    # Assert the response data
    data = json.loads(response.data)
    assert data == {"message": "Pong!"}


def test_test_db(client):
    # Make a request to the '/test_db' route
    response = client.get("/test_db")

    # Check that the status code is 200 (OK)
    assert response.status_code == 200


# def test_test_db_success(client):
#     # Mock the database connection to return fake data for the test
#     fake_data = [
#         ("John Doe", 1),
#         ("Jane Smith", 2),
#     ]  # Example data from the 'user' table

#     with patch("app.routes.general.get_db_connection") as mock_db:
#         # Mock the cursor and the execute/fetchall behavior
#         mock_cursor = mock_db.return_value.cursor.return_value
#         mock_cursor.fetchall.return_value = fake_data

#         # Send a GET request to the /test_db endpoint
#         response = client.get("/test_db")

#         # Assert the response status code
#         assert response.status_code == 200

#         # Assert the response data matches the fake data
#         data = json.loads(response.data)
#         assert data == fake_data


# def test_test_db_failure(client):
#     # Mock the database connection to simulate an error
#     with patch("app.routes.general.get_db_connection") as mock_db:
#         # Simulate an exception during database connection
#         mock_db.side_effect = Exception("Database connection failed")

#         # Send a GET request to the /test_db endpoint
#         response = client.get("/test_db")

#         # Assert the response status code is 200 (error handled in the route)
#         assert response.status_code == 200

#         # Assert the response contains the error message
#         data = json.loads(response.data)
#         assert data == {"error": "Database connection failed"}
