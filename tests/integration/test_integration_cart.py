import requests
from rest_framework import status

API_URL = "http://127.0.0.1:8000/api"
headers = {"Authorization": "Token 891b507a2b2057228d804ced2824f7f36e0fbab9"}


def test_get():
    request = requests.get(API_URL + "/cart/")

    assert request.status_code == status.HTTP_200_OK
    assert request.status_code != status.HTTP_405_METHOD_NOT_ALLOWED
    assert request.status_code != status.HTTP_401_UNAUTHORIZED
    assert request.status_code != status.HTTP_403_FORBIDDEN
    assert request.status_code != status.HTTP_404_NOT_FOUND
    assert request.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR
