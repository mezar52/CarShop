import django_filters.rest_framework
from django.shortcuts import get_object_or_404
from rest_framework import generics, status
from rest_framework.filters import SearchFilter
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from apistore.invoices import create_invoice, verify_signature
from apistore.serializers import (
    CarSerializer,
    DealershipSerializer,
    CarTypeSerializer,
    OrderSerializer,
)
from store.models import Car, Dealership, CarType, Client, Order, OrderQuantity


class CustomPageNumberPagination(PageNumberPagination):
    page_size = 100


class CarTypeViewSet(
    generics.ListAPIView,
    generics.RetrieveAPIView,
    generics.CreateAPIView,
    GenericViewSet,
):
    queryset = CarType.objects.all()
    serializer_class = CarTypeSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]


class CarViewSet(
    generics.ListAPIView,
    generics.RetrieveAPIView,
    generics.CreateAPIView,
    GenericViewSet,
):
    queryset = Car.objects.filter(owner__isnull=True, blocked_by_order__isnull=True)
    serializer_class = CarSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [django_filters.rest_framework.DjangoFilterBackend, SearchFilter]
    filterset_fields = ["year"]
    search_fields = ["car_type__name"]

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class DealersViewSet(
    generics.ListAPIView,
    generics.RetrieveAPIView,
    generics.CreateAPIView,
    GenericViewSet,
):
    queryset = Dealership.objects.all()
    serializer_class = DealershipSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ["name"]


class CreateOrderView(
    generics.ListAPIView,
    generics.RetrieveAPIView,
    GenericViewSet,
):
    queryset = Car.objects.filter(owner__isnull=True, blocked_by_order__isnull=True)
    serializer_class = CarSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticatedOrReadOnly]

    @staticmethod
    def post(request, pk):
        car = get_object_or_404(Car, pk=pk)
        client = Client.objects.first()
        car_type = car.car_type
        dealership = car_type.dealerships.first()

        order = Order.objects.filter(client=client, is_paid=False).first()

        if not order:
            order = Order.objects.create(
                client=client, dealership=dealership, is_paid=False
            )

        order_quantity, created = OrderQuantity.objects.get_or_create(
            order=order, car_type=car_type
        )

        if not created:
            order_quantity.quantity += 1
            order_quantity.save()

        car.block(order)
        client.order_cart.add(car)

        return Response(
            {"message": "Cars added to the cart"}, status=status.HTTP_201_CREATED
        )


class CartView(generics.ListAPIView, generics.RetrieveAPIView, GenericViewSet):
    queryset = Order.objects.filter(is_paid=False)
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def post(self, request, *args, **kwargs):
        order = self.get_object()

        if not order.is_paid:
            client = order.client
            cars = Car.objects.filter(blocked_by_order=order)

            for car in cars:
                car.sell()
                car.owner = client
                car.save()

            create_invoice(order, reverse("webhook-mono", request=request))
            return Response(
                {"invoice": order.invoice_url, "message": "Your invoice"},
                status=status.HTTP_200_OK,
            )

    def delete(self, request, *args, **kwargs):
        order = self.get_object()
        cars = Car.objects.filter(blocked_by_order=order)

        for car in cars:
            car.unblock()
            car.owner = None
            car.save()

        client = Client.objects.first()
        client.order_cart.clear()
        order.delete()

        return Response({"message": "The order was successfully canceled"})


class MonoAcquiringWebhookReceiver(APIView):
    def post(self, request):
        try:
            verify_signature(request)
        except Exception as e:
            return Response({"status": "error"}, status=400)
        reference = request.data.get("reference")
        order = Order.objects.get(id=reference)
        if order.order_id != request.data.get("invoiceId"):
            return Response({"status": "error"}, status=400)
        order.status = request.data.get("status", "error")
        order.save()

        if order.status == "success":
            order.is_paid = True
            order.status = "paid"
            order.save()

            client = Client.objects.first()
            client.order_cart.clear()
            return Response({"status": "Paid"}, status=200)
        return Response({"status": "ok"})
