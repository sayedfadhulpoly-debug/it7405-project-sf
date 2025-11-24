from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Review, Appointment
from .models import Order, Offer, Review, Appointment, Car


class CustomUserCreationForm(UserCreationForm):
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")
        help_texts = {
            "username": "",
            "email": "",
            "password1": "",
            "password2": "",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap class to username & password fields
        for field_name, field in self.fields.items():
            if field.widget.attrs.get("class") is None:
                field.widget.attrs["class"] = "form-control"


from django import forms
from .models import Order, Offer

class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['full_name', 'email', 'phone', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class OfferForm(forms.ModelForm):
    class Meta:
        model = Offer
        fields = ['amount', 'message']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['full_name', 'email', 'rating', 'comment']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            # We hide this input – our stars will control it
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }





class AppointmentForm(forms.ModelForm):
    # Dropdown for cars
    car_interest = forms.ChoiceField(
        choices=[],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label="Car you want to test drive",
        required=True,
    )

    class Meta:
        model = Appointment
        fields = ['full_name', 'email', 'phone', 'car_interest',
                  'preferred_date', 'preferred_time', 'message']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'preferred_time': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        cars = Car.objects.all().order_by('make', 'model', 'year')
        self.fields['car_interest'].choices = [
            (
                f"{car.make} {car.model} ({car.year})",
                f"{car.make} {car.model} ({car.year})"
            )
            for car in cars
        ]

        if not self.fields['car_interest'].choices:
            self.fields['car_interest'].choices = [("", "No cars available")]
            self.fields['car_interest'].widget.attrs['disabled'] = True





class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "username"]
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "username": forms.TextInput(attrs={"class": "form-control"}),
        }
