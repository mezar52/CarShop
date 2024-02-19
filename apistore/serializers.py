from django.db.models import Sum
from rest_framework import serializers

from store.models import Car, CarType, Dealership, Order


class CarTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarType
        fields = ["id", "name", "brand", "price"]


class DealershipSerializer(serializers.ModelSerializer):
    # available_car_types = serializers.PrimaryKeyRelatedField(queryset=CarType.objects.all(),many=True)

    class Meta:
        model = Dealership
        fields = ["id", "name", "available_car_types"]


class CarSerializer(serializers.ModelSerializer):
    car_type_details = CarTypeSerializer(source="car_type", read_only=True)

    class Meta:
        model = Car
        fields = [
            "id",
            "car_type",
            "color",
            "year",
            "image",
            "car_type_details",
        ]


class OrderSerializer(serializers.ModelSerializer):
    price = serializers.SerializerMethodField()
    qty = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ["id", "client", "dealership", "is_paid", "price", "qty"]

    @staticmethod
    def get_price(obj: Order):
        amount = 0
        for qty in obj.car_types.all():
            sum_ = qty.car_type.price * qty.quantity
            amount += sum_
        return amount

    @staticmethod
    def get_qty(obj: Order):
        order_quantity = obj.car_types.aggregate(Sum("quantity"))
        return order_quantity["quantity__sum"] if order_quantity else None


class OrderQuantitySerializer(serializers.Serializer):
    car = serializers.IntegerField()
    quantity = serializers.IntegerField()


class OrderInputSerializer(serializers.Serializer):
    order = OrderQuantitySerializer(many=True)
