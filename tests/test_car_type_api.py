import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from samples import sample_user
from store.models import CarType


@pytest.mark.django_db
def test_car_type_get(sample_user):
    url = reverse("car-type-list")
    response = sample_user.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db(transaction=True)
def test_car_type_get_detail(sample_user):
    car_type1 = CarType.objects.create(id=1, name="X5", brand="BMW", price=90000)
    car_type2 = CarType.objects.create(id=2, name="R8", brand="AUDI", price=100000)

    url = reverse("car-type-detail", args=[car_type1.id])
    response = sample_user.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.status_code != status.HTTP_404_NOT_FOUND
    assert response.json()["id"] != car_type2
    assert response.json() == {"id": 1, "name": "X5", "brand": "BMW", "price": 90000}


@pytest.mark.django_db
def test_user_is_not_authenticate(sample_user):
    client = APIClient()
    url = reverse("car-type-list")
    data = {"name": "X3", "brand": "BMW", "price": 80000}
    response_get = client.get(url)
    response_post = client.post(url, data)

    assert response_get.status_code == status.HTTP_200_OK
    assert response_post.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_car_type_post(sample_user):
    url = reverse("car-type-list")
    data = {"name": "X3", "brand": "BMW", "price": 80000}
    response = sample_user.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"id": 1, "name": "X3", "brand": "BMW", "price": 80000}


@pytest.mark.django_db
def test_method_not_allowed(sample_user):
    car_type = CarType.objects.create(id=1, name="X5", brand="BMW", price=90000)
    data = {"id": 1, "name": "X3", "brand": "BMW", "price": 80000}
    url = reverse("car-type-detail", args=[car_type.id])

    response_put = sample_user.put(url, data)
    response_delete = sample_user.delete(url)

    assert response_put.status_code != status.HTTP_200_OK
    assert response_delete.status_code != status.HTTP_204_NO_CONTENT
    assert response_put.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response_delete.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
