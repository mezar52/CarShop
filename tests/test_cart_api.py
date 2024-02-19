import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from samples import sample_user
from store.models import CarType, Dealership, Client, Order, Car

client = APIClient()


@pytest.mark.django_db(transaction=True)
def test_get_cart_detail(sample_user):
    car_type = CarType.objects.create(name="X5", brand="BMW", price=90000)
    client_ = Client.objects.create(
        name="John", email="john@example.com", phone="123456789"
    )
    car = Car.objects.create(car_type=car_type, color="Black", year=2022, owner=client_)
    order = Order.objects.create(
        client=client_, dealership=Dealership.objects.create(name="Dealer")
    )
    order.reserved_cars.add(car)

    url = reverse("cart-detail", kwargs={"pk": order.pk})
    response = sample_user.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.status_code != status.HTTP_401_UNAUTHORIZED
    assert response.status_code != status.HTTP_403_FORBIDDEN
    assert response.status_code != status.HTTP_404_NOT_FOUND
    assert response.status_code != status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR


@pytest.mark.django_db(transaction=True)
def test_delete_order(sample_user):
    car_type = CarType.objects.create(name="X5", brand="BMW", price=90000)
    client_ = Client.objects.create(
        name="John", email="john@example.com", phone="123456789"
    )
    car = Car.objects.create(car_type=car_type, color="Black", year=2022, owner=client_)
    order = Order.objects.create(
        client=client_, dealership=Dealership.objects.create(name="Dealer")
    )
    order.reserved_cars.add(car)

    url = reverse("cart-detail", kwargs={"pk": order.pk})
    response = sample_user.delete(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.status_code != status.HTTP_401_UNAUTHORIZED
    assert response.status_code != status.HTTP_403_FORBIDDEN
    assert response.status_code != status.HTTP_404_NOT_FOUND
    assert response.status_code != status.HTTP_405_METHOD_NOT_ALLOWED
    assert response.status_code != status.HTTP_500_INTERNAL_SERVER_ERROR
    car.refresh_from_db()
    assert car.blocked_by_order is None
    assert not Order.objects.filter(pk=order.pk).exists()
    assert response.data == {"message": "The order was successfully canceled"}
