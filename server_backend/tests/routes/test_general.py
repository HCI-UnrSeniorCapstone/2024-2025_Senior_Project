import os
import pytest
from unittest.mock import patch
import json
from app import create_app
from app.utility.db_connection import get_db_connection


def test_ping_code(client):
    response = client.get("/ping")
    assert response.status_code == 200


def test_ping_message(client):
    response = client.get("/ping")
    data = json.loads(response.data)
    assert data == {"message": "Pong!"}


def test_test_db_code(client):
    response = client.get("/test_db")
    assert response.status_code == 200


def test_test_db_message(client):
    response = client.get("/test_db")
    assert response.data == "hi"
