import os
import random

import boto3
from django.core.files import File
from django.core.management.base import BaseCommand

from carshop import settings
from store.models import Client, CarType, Car, Dealership

CAR_TYPES = [
    {
        "name": "X5",
        "brand": "BMW",
        "price": "100000",
        "dealership": "BMW-Dealer",
        "color": "Black",
        "image": "store/images/x5black.png",
    },
    {
        "name": "R8",
        "brand": "AUDI",
        "price": "90000",
        "dealership": "AUDI-Dealer",
        "color": "White",
        "image": "store/images/r8white.png",
    },
    {
        "name": "Bentayga",
        "brand": "Bentley",
        "price": "110000",
        "dealership": "Bentley-Dealer",
        "color": "Red",
        "image": "store/images/bbred.png",
    },
    {
        "name": "AMG",
        "brand": "Mercedes",
        "price": "200000",
        "dealership": "Mercedes-Dealer",
        "color": "Green",
        "image": "store/images/amggreen.png",
    },
]


class Command(BaseCommand):
    help = "Create demo data"

    def handle(self, *args, **options):
        Client.objects.all().delete()
        CarType.objects.all().delete()
        Dealership.objects.all().delete()
        Car.objects.all().delete()

        Client.objects.create(
            name="Oleksandr", email="alex@example.com", phone="+380667676769"
        )

        for car_type_data in CAR_TYPES:
            car_type = CarType.objects.create(
                name=car_type_data["name"],
                brand=car_type_data["brand"],
                price=car_type_data["price"],
            )

            for _ in range(4):
                car_image_path = car_type_data["image"]
                with open(car_image_path, "rb") as car_image_file:
                    session = boto3.Session(
                        aws_access_key_id=settings.AWS_S3_ACCESS_KEY_ID,
                        aws_secret_access_key=settings.AWS_S3_SECRET_ACCESS_KEY,
                        region_name=settings.AWS_S3_REGION_NAME,
                    )
                    session.resource("s3")

                    car_image_name = os.path.basename(car_image_path)

                    car_image_field = File(car_image_file, car_image_name)
                    car_image_field.name = f"car_images/{car_image_name}"

                    Car.objects.create(
                        car_type=car_type,
                        color=car_type_data["color"],
                        year=random.randint(2000, 2024),
                        image=car_image_field,
                    )

            obj, created = Dealership.objects.get_or_create(
                name=car_type_data["dealership"]
            )
            obj.available_car_types.add(car_type)

        self.stdout.write(self.style.SUCCESS("The data was successfully generated"))
