import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from samples import sample_user
from store.models import CarType, Car


@pytest.mark.django_db
def test_get_cars(sample_user):
    url = reverse("car-list")
    response = sample_user.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_user_is_not_authenticate():
    client = APIClient()
    url = reverse("car-list")
    car_type = CarType.objects.create(id=1, name="X5", brand="BMW", price=90000)
    data = {
        "car_type": car_type.id,
        "color": "Black",
        "year": 2024,
        "image": "",
    }
    response = client.post(url, data)

    assert response.status_code != status.HTTP_201_CREATED
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_post_car(sample_user):
    car_type = CarType.objects.create(id=1, name="X5", brand="BMW", price=90000)
    data = {
        "car_type": car_type.id,
        "color": "Black",
        "year": 2024,
        "image": "",
    }

    url = reverse("car-list")
    response = sample_user.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.status_code != status.HTTP_400_BAD_REQUEST
    assert response.status_code != status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_bad_request(sample_user):
    car_type = CarType.objects.create(id=1, name="X5", brand="BMW", price=90000)
    data = {
        "car_type": car_type.id,
        "color": "Black",
        "year": "",
        "image": "",
    }

    url = reverse("car-list")
    response = sample_user.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.status_code != status.HTTP_201_CREATED
    assert response.status_code != status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_car_update(sample_user):
    car_type = CarType.objects.create(id=1, name="X5", brand="BMW", price=90000)
    car = Car(car_type=car_type, color="Black", year="2024", image=None)
    car.save()
    data = {
        "car_type": car_type.id,
        "color": "Rad",
        "year": 2025,
        "image": "",
    }

    url = reverse("car-detail", args=[car.id])
    response = sample_user.put(url, data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["color"] == "Rad"
    assert response.status_code != status.HTTP_401_UNAUTHORIZED
    assert response.status_code != status.HTTP_404_NOT_FOUND
    assert response.status_code != status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_method_not_allowed(sample_user):
    car_type = CarType.objects.create(id=1, name="X5", brand="BMW", price=90000)
    car = Car(car_type=car_type, color="Black", year="2024", image=None)
    car.save()

    url = reverse("car-detail", args=[car.id])
    response = sample_user.delete(url)

    assert response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.status_code != status.HTTP_204_NO_CONTENT
