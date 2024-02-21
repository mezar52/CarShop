import pytest
import requests
from rest_framework import status

API_URL = "http://127.0.0.1:8000/api"
headers = {"Authorization": "Token 891b507a2b2057228d804ced2824f7f36e0fbab9"}


@pytest.fixture
def api_client():
    return requests.Session()


def test_get():
    request = requests.get(API_URL + "/types-api/")

    assert request.status_code == status.HTTP_200_OK
    assert request.status_code != status.HTTP_401_UNAUTHORIZED
    assert request.status_code != status.HTTP_403_FORBIDDEN
    assert request.status_code != status.HTTP_405_METHOD_NOT_ALLOWED
    assert request.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


def test_get_ditail():
    request = requests.get(API_URL + "/types-api/1/")

    assert request.status_code == status.HTTP_200_OK
    assert request.status_code != status.HTTP_401_UNAUTHORIZED
    assert request.status_code != status.HTTP_403_FORBIDDEN
    assert request.status_code != status.HTTP_404_NOT_FOUND
    assert request.status_code != status.HTTP_405_METHOD_NOT_ALLOWED
    assert request.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


def test_user_has_no_permission():
    request = requests.post(
        API_URL + "/types-api/", json={"name": "Name", "brand": "Brand", "price": 1}
    )

    assert request.status_code == status.HTTP_401_UNAUTHORIZED
    assert request.status_code != status.HTTP_201_CREATED
    assert request.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


def test_bad_request(api_client):
    request = api_client.post(API_URL + "/types-api/", json={}, headers=headers)

    assert request.status_code == status.HTTP_400_BAD_REQUEST
    assert request.status_code != status.HTTP_201_CREATED
    assert request.status_code != status.HTTP_401_UNAUTHORIZED
    assert request.status_code != status.HTTP_403_FORBIDDEN
    assert request.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


def test_update(api_client):
    request = api_client.put(
        API_URL + "/types-api/1/",
        json={"name": "Name", "brand": "Brand", "price": 1},
        headers=headers,
    )

    assert request.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert request.status_code != status.HTTP_200_OK
    assert request.status_code != status.HTTP_401_UNAUTHORIZED
    assert request.status_code != status.HTTP_403_FORBIDDEN
    assert request.status_code != status.HTTP_404_NOT_FOUND
    assert request.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


def test_delete(api_client):
    request = api_client.put(API_URL + "/types-api/1/", headers=headers)

    assert request.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert request.status_code != status.HTTP_204_NO_CONTENT
    assert request.status_code != status.HTTP_401_UNAUTHORIZED
    assert request.status_code != status.HTTP_403_FORBIDDEN
    assert request.status_code != status.HTTP_404_NOT_FOUND
    assert request.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR
