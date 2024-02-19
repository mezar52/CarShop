import uuid

from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.files.base import ContentFile
from django.core.mail import send_mail
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.core.signing import Signer, BadSignature
from django.db.models import Q
from django.shortcuts import render, redirect, get_object_or_404
from rest_framework.reverse import reverse

from apistore.invoices import create_invoice
from store.forms import (
    ClientForm,
    CarTypeForm,
    CarForm,
    DealershipForm,
    UserCreationFormWithEmail,
    ImageForm,
)
from store.models import Car, CarType, Dealership, Client, Order, OrderQuantity, Image

""" --- CLIENT PART --- """


def create_client(request):
    if request.method == "GET":
        form = ClientForm()
        return render(request, "add_or_create/add_client.html", {"client": form})

    form = ClientForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("redirect_on_store_page")

    return render(request, "add_or_create/add_client.html", {"client": form})


def send_activation_email(request, user: User):
    user_signed = Signer().sign(user.id)
    signed_url = request.build_absolute_uri(f"/activate/{user_signed}")
    send_mail(
        "Registration complete",
        "Click here to activate your account: " + signed_url,
        "1dlcastra@gmail.com",
        [user.email],
        fail_silently=False,
    )


def register_view(request):
    if request.method == "GET":
        form = UserCreationFormWithEmail()
        return render(request, "registration/register.html", {"form": form})

    form = UserCreationFormWithEmail(request.POST)
    if form.is_valid():
        form.instance.is_active = False
        form.save()
        send_activation_email(request, form.instance)
        return redirect("login_view")

    return render(request, "registration/register.html", {"form": form})


def logout_view(request):
    logout(request)
    return redirect("login_view")


def activate(request, user_signed):
    try:
        user_id = Signer().unsign(user_signed)
    except BadSignature:
        return redirect("login_view")
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect("login_view")
    user.is_active = True
    user.save()
    return redirect("login_view")


def redirect_on_store_page(request):
    car_list = Car.objects.filter(owner__isnull=True, blocked_by_order__isnull=True)

    search_query = request.GET.get("search", "")
    if search_query:
        car_list = car_list.filter(Q(car_type__name__icontains=search_query))

    year_query = request.GET.get("year", "")
    if year_query:
        car_list = car_list.filter(year=year_query)

    page = request.GET.get("page", 1)
    paginator = Paginator(car_list, 36)
    try:
        cars = paginator.page(page)
    except PageNotAnInteger:
        cars = paginator.page(1)
    except EmptyPage:
        cars = paginator.page(paginator.num_pages)

    return render(
        request,
        "store_page.html",
        {"cars": cars, "search_query": search_query, "year_query": year_query},
    )


@login_required
def create_order(request, pk):
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

    return redirect("redirect_on_store_page")


def get_total_price(order):
    amount = 0
    for qty in order.car_types.all():
        sum_ = qty.car_type.price * qty.quantity
        amount += sum_
    return amount


def view_cart(request):
    if request.method == "GET":
        return redirect(redirect_on_store_page)
    if request.method == "POST":
        client = Client.objects.first()
        user_cars = client.order_cart.all()
        order = Order.objects.filter(client=client, is_paid=False).first()
        total_price = get_total_price(order) if order else 0
        return render(
            request,
            "show_or_get/cart_page.html",
            {"user_cars": user_cars, "order": order, "total_price": total_price},
        )


@login_required
def pay_order(request, pk):
    order = get_object_or_404(Order, pk=pk)

    if request.method == "GET":
        return render(request, "show_or_get/order_success.html")

    if request.method == "POST":
        if not order.is_paid:
            client = order.client
            cars = Car.objects.filter(blocked_by_order=order)

            for car in cars:
                car.sell()
                car.owner = client
                car.save()

            create_invoice(order, reverse("webhook-mono", request=request))
            return redirect(order.invoice_url)

        if order.status == "paid":
            return render(request, "show_or_get/order_success.html")


@login_required
def cancel_order(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.method == "GET":
        return render(request, "show_or_get/order_cancel.html")

    if request.method == "POST":
        cars = Car.objects.filter(blocked_by_order=order)
        for car in cars:
            car.unblock()
        client = Client.objects.first()
        client.order_cart.clear()
        order.delete()

        return render(request, "show_or_get/order_cancel.html")

    return render(request, "show_or_get/order_cancel.html")


""" --- STAFF PART --- """


# ADD METHODS


def add_new_car_type(request):
    if request.method == "GET":
        form = CarTypeForm()
        return render(request, "add_or_create/add_car_type.html", {"car_type": form})

    form = CarTypeForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("get_all_types_of_cars")

    return render(request, "add_or_create/add_car_type.html", {"car_type": form})


@login_required
def add_image(request):
    if request.method == "GET":
        form = ImageForm()
        return render(request, "add_or_create/add_image.html", {"form": form})

    form = ImageForm(request.POST, request.FILES)
    if form.is_valid():
        name = form.cleaned_data["name"]
        image = form.cleaned_data["image"]

        car_image = Image.objects.create(name=name, image=image)
        car_image.name = name
        car_image.image.save(f"{uuid.uuid4().hex}.png", ContentFile(image.read()))
        return render(
            request, "add_or_create/add_image.html", {"form": form, "image": car_image}
        )

    return render(request, "add_or_create/add_image.html", {"form": form})


def add_new_car(request):
    if request.method == "GET":
        form = CarForm()
        return render(request, "add_or_create/add_car.html", {"car": form})

    form = CarForm(request.POST, request.FILES)
    if form.is_valid():
        car_type_instance = form.save(commit=False)
        if "image" in request.FILES:
            car_type_instance.image = request.FILES["image"]

        car_type_instance.save()
        form.save()
        return redirect("get_all_cars")

    return render(request, "add_or_create/add_car.html", {"car": form})


def add_dealership(request):
    if request.method == "GET":
        form = DealershipForm()
        return render(request, "add_or_create/add_dealership.html", {"dealer": form})

    form = DealershipForm(request.POST)
    if form.is_valid():
        form.save()
        return redirect("get_all_dealership")

    return render(request, "add_or_create/add_dealership.html", {"dealer": form})


# EDIT METHODS


@login_required
def edit_car(request, pk):
    car = get_object_or_404(Car, pk=pk)
    if request.method == "GET":
        form = CarForm(instance=car)
        return render(request, "updata_or_edit/edit_car.html", {"car": form})

    form = CarForm(request.POST, request.FILES, instance=car)
    if "edit" in request.POST:
        car_instance = form.save(commit=False)
        if "image" in request.FILES:
            car_instance.image = request.FILES["image"]

        car_instance.save()
        form.save()
        return redirect("get_all_cars")

    return render(request, "updata_or_edit/edit_car.html", {"car": form})


# GET METHODS
def get_all_types_of_cars(request):
    if request.method == "GET":
        car_type_list = CarType.objects.all()
        return render(
            request, "show_or_get/all_types_of_cars.html", {"car_type": car_type_list}
        )


def get_all_cars(request):
    car_list = Car.objects.all()
    return render(request, "show_or_get/all_cars.html", {"car": car_list})


def get_all_dealership(request):
    dealership_list = Dealership.objects.all()

    search_query = request.GET.get("search", "")
    if search_query:
        dealership_list = dealership_list.filter(Q(name=search_query))

    page = request.GET.get("page", 1)
    paginator = Paginator(dealership_list, 36)
    try:
        dealers = paginator.page(page)
    except PageNotAnInteger:
        dealers = paginator.page(1)
    except EmptyPage:
        dealers = paginator.page(paginator.num_pages)
    return render(
        request,
        "show_or_get/all_dealers.html",
        {
            "dealer_list": dealership_list,
            "dealers": dealers,
            "search_query": search_query,
        },
    )
    
