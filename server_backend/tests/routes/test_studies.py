import pytest
from unittest.mock import patch


def test_get_study_data_code_success(client):
    response = client.get("/get_study_data/1")
    assert response.status_code == 200


def test_get_study_data_code_fail_no_user(client):
    response = client.get("/get_study_data/1000")
    assert response.status_code == 404


def test_load_study_success(client):
    response = client.get("/load_study/1")
    assert response.status_code == 200


def test_load_study_fail(client):
    response = client.get("/load_study/1000")
    assert response.status_code == 500


def test_delete_study_success(client):
    response = client.post("/delete_study/1/1")
    assert response.status_code == 200


def test_delete_study_fail_not_owner(client):
    response = client.post("/delete_study/10/1")
    assert response.status_code == 403
