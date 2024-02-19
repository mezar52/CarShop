from django.contrib.auth.views import LoginView
from django.urls import path, include

from store import views

urlpatterns = [
    path("accounts/", include("allauth.urls")),
    path("accounts/google/", include("allauth.socialaccount.urls"), name="auth_google"),
    path("", views.register_view, name="register_view"),
    path("login/", LoginView.as_view(), name="login_view"),
    path("logout/", views.logout_view, name="logout_view"),
    path("activate/<user_signed>", views.activate, name="activate"),
    path("store-page/", views.redirect_on_store_page, name="redirect_on_store_page"),
    path("create_order/<int:pk>/", views.create_order, name="create_order"),
    path("cart/", views.view_cart, name="view_cart"),
    path("pay_order/<int:pk>", views.pay_order, name="pay_order"),
    path("cancel_order/<int:pk>", views.cancel_order, name="cancel_order"),
    # ADD
    path("create-client/", views.create_client, name="register_client"),
    path(
        "for-staff-only/add-new-car-type/",
        views.add_new_car_type,
        name="add_new_car_type",
    ),
    path("for-staff-only/add-new-car/", views.add_new_car, name="add_new_car"),
    path("for-staff-only/add-dealer/", views.add_dealership, name="add_dealership"),
    path("for-staff-only/add-image/", views.add_image, name="add_image"),
    # GET
    path(
        "for-staff-only/get-all-types/",
        views.get_all_types_of_cars,
        name="get_all_types_of_cars",
    ),
    path("for-staff-only/get-all-cars/", views.get_all_cars, name="get_all_cars"),
    path(
        "for-staff-only/get-all-dealers/",
        views.get_all_dealership,
        name="get_all_dealership",
    ),
    # EDIT
    path("for-staff-only/edit-car/<int:pk>", views.edit_car, name="edit_car"),
]
