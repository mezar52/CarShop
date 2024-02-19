import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from samples import sample_user
from store.models import Dealership, CarType, Client


@pytest.mark.django_db
def test_get_dealers(sample_user):
    url = reverse("dealers-list")
    response = sample_user.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db(transaction=True)
def test_get_dealer_detail(sample_user):
    user = Client.objects.create(
        name="User", email="ex@gmail.com", phone="+380667171304"
    )
    car_type = CarType.objects.create(id=1, name="X5", brand="BMW", price=90000)
    dealer = Dealership.objects.create(id=1, name="Dealer")
    dealer.clients.add(user)
    dealer.available_car_types.set([car_type.id])

    url = reverse("dealers-detail", args=[dealer.id])
    response = sample_user.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.status_code != status.HTTP_404_NOT_FOUND
    assert response.json()["id"] == dealer.id
    assert response.json() == {"id": 1, "name": "Dealer", "available_car_types": [1]}


@pytest.mark.django_db
def test_user_is_not_authenticate():
    client = APIClient()
    url = reverse("dealers-list")
    response = client.post(url)

    assert response.status_code != status.HTTP_201_CREATED
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_post_dealer(sample_user):
    car_type = CarType.objects.create(id=1, name="X5", brand="BMW", price=90000)
    url = reverse("dealers-list")
    data = {
        "name": "NewDealer",
        "available_car_types": [car_type.id],
    }

    response = sample_user.post(url, data)

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {"id": 1, "name": "NewDealer", "available_car_types": [1]}


@pytest.mark.django_db(transaction=True)
def test_method_not_allowed(sample_user):
    dealer_client = Client.objects.create(
        name="User", email="ex1@gmail.com", phone="+380667171304"
    )
    car_type = CarType.objects.create(id=1, name="R8", brand="AUDI", price=90000)
    dealer = Dealership.objects.create(id=1, name="Dealer")
    dealer.clients.add(dealer_client)
    dealer.available_car_types.set([car_type.id])

    url = reverse("dealers-detail", args=[dealer.id])
    data = {
        "name": "NewDealer1",
        "available_car_types": [car_type.id],
    }

    response_put = sample_user.put(url, data)
    response_delete = sample_user.delete(url)

    assert response_put.status_code != status.HTTP_200_OK
    assert response_delete.status_code != status.HTTP_204_NO_CONTENT
    assert response_put.status_code == status.HTTP_405_METHOD_NOT_ALLOWED
    assert response_delete.status_code == status.HTTP_405_METHOD_NOT_ALLOWED


@pytest.mark.django_db
def test_bed_request(sample_user):
    car_type = CarType.objects.create(id=1, name="X5", brand="BMW", price=90000)

    url = reverse("dealers-list")
    data = {
        "name": "",
        "available_car_types": [car_type.id],
    }

    response = sample_user.post(url, data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
