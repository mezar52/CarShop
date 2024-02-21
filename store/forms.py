import phonenumbers

from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import EmailField

from store.models import Client, CarType, Car, Dealership, Image


class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ["name", "email", "phone"]
        labels = {
            "name": "Ім'я",
            "email": "Електронна пошта",
            "phone": "Номер телефону",
        }

    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) > 50:
            raise forms.ValidationError(
                "Name is too long, max length is 50/Ім'я занадто вилеке, максимальна довжина 50"
            )

        if any(char.isdigit() for char in name):
            raise forms.ValidationError(
                "The name must not contain any numbers/Ім'я не повинно мати цифр"
            )

        return name

    def clean_email(self):
        email = self.cleaned_data["email"]
        if len(email) > 254:
            raise forms.ValidationError(
                "The e-mail address is too long/Адреса електронної пошти занадто довга"
            )

        return email

    def clean_phone(self):
        phone = self.cleaned_data["phone"]
        if not phone:
            raise forms.ValidationError(
                "Phone cannot be empty/Поле телефон не може бути пустим"
            )

        if len(phone) < 9:
            raise forms.ValidationError(
                "The number provided is too short/Наданий номер занадто короткий"
            )

        try:
            parsed = phonenumbers.parse(phone, None)
        except phonenumbers.NumberParseException as error:
            raise forms.ValidationError(
                f"{error.args[0]}/Наданий рядок, схоже, не був номером телефону "
            )

        formatted_phone = phonenumbers.format_number(
            parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL
        )
        return formatted_phone


class CarTypeForm(forms.ModelForm):
    class Meta:
        model = CarType
        fields = ["name", "brand", "price"]
        labels = {
            "name": "Назва авто",
            "brand": "Марка авто",
            "price": "Ціна",
        }

    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) > 50:
            raise forms.ValidationError(
                "Name is too long, max length is 50/Назва занадто вилекa, максимальна довжина 50"
            )
        return name

    def clean_brand(self):
        brand = self.cleaned_data["brand"]
        if len(brand) > 50:
            raise forms.ValidationError(
                "Brand name is too long, max length is 50/Назва бренду занадто вилекa, максимальна довжина 50"
            )
        return brand


class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        fields = ["car_type", "color", "year", "image"]
        labels = {
            "car_type": "Тип авто",
            "color": "Колір",
            "year": "Рік",
            "image": "Фото",
        }

    def clean_color(self):
        color = self.cleaned_data["color"]
        if len(color) > 50:
            raise forms.ValidationError(
                "Color name is too long, max length is 50/Назва кольору занадто вилекa, максимальна довжина 50"
            )

        if any(char.isdigit() for char in color):
            raise forms.ValidationError(
                "The color name must not contain any numbers/Назва кольору не повинно мати цифр"
            )
        return color

    def clean_year(self):
        year = self.cleaned_data["year"]
        if len(str(year)) < 4:
            raise forms.ValidationError(
                "Specify the full year of manufacture of the car/Вкажіть повний рік випуску авто "
            )

        return year


class DealershipForm(forms.ModelForm):
    class Meta:
        model = Dealership
        fields = ["name", "available_car_types"]
        labels = {"name": "Дилерство"}

    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) > 50:
            raise forms.ValidationError(
                "Name is too long, max length is 50/Назва занадто вилекa, максимальна довжина 50"
            )
        return name


class UserCreationFormWithEmail(UserCreationForm):
    email = EmailField(label="Email address", required=True, help_text="Required.")

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class ImageForm(forms.ModelForm):
    class Meta:
        model = Image
        fields = ["name", "image"]
        labels = {"name": "Назва авто", "image": "Фото"}

    def clean_name(self):
        name = self.cleaned_data["name"]
        if len(name) > 50:
            raise forms.ValidationError(
                "Name is too long, max length is 50/Назва занадто вилекa, максимальна довжина 50"
            )
        return name
