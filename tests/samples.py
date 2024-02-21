from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from store.models import CarType, Car


@pytest.fixture(scope="function")
def sample_car_type():
    car_type = CarType.objects.create(name="X5", brand="BMW", price=90000)
    return car_type


@pytest.fixture(scope="function")
def sample_car(sample_car_type):
    car = Car.objects.create(
        car_type=sample_car_type, color="Black", year=2024, image=None
    )
    return car


@pytest.fixture(scope="function")
def sample_user():
    client = APIClient()
    user = User(username="User", password="UserPassword")
    client.force_authenticate(user)
    return client


@pytest.fixture
def mock_create_invoice(request):
    with patch("apistore.invoices.create_invoice") as mock_create_invoice:
        yield mock_create_invoice
