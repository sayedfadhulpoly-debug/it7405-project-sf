from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from bson import ObjectId
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import Car, Review, Appointment
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.contrib import messages

from django.http import HttpResponseForbidden, Http404
from bson.errors import InvalidId

from .forms import UserUpdateForm


from .models import Car, Order, Offer, Review, Appointment
from .forms import (
    CustomUserCreationForm,
    OrderForm,
    OfferForm,
    ReviewForm,
    AppointmentForm,
)

def mongo_pk_or_404(hex_id):
    """
    Convert a hex string to a Mongo ObjectId, or raise 404 if invalid.
    """
    try:
        return ObjectId(hex_id)
    except InvalidId:
        raise Http404("Invalid object ID.")



def home(request):
    total_cars = Car.objects.count()
    total_reviews = Review.objects.count()
    total_appointments = Appointment.objects.count()

    context = {
        'total_cars': total_cars,
        'total_reviews': total_reviews,
        'total_appointments': total_appointments,
    }
    return render(request, 'cars/home.html', context)




def signup(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = form.cleaned_data.get("first_name")
            user.last_name  = form.cleaned_data.get("last_name")
            user.email      = form.cleaned_data.get("email")
            user.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/signup.html', {'form': form})



def car_list(request):
    q = request.GET.get('q')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    year = request.GET.get('year')

    cars = Car.objects.all()

    if q:
        cars = cars.filter(
            Q(make__icontains=q) |
            Q(model__icontains=q)
        )

    if min_price:
        cars = cars.filter(price__gte=min_price)

    if max_price:
        cars = cars.filter(price__lte=max_price)

    if year:
        cars = cars.filter(year=year)

    return render(request, 'cars/car_list.html', {'cars': cars})


def car_detail(request, id):
    car = Car.objects.get(_id=ObjectId(id))

    # Get other cars (exclude current one)
    other_cars = Car.objects.filter().exclude(_id=ObjectId(id))[:6]  # limit to 6

    return render(request, 'cars/car_detail.html', {
        'car': car,
        'other_cars': other_cars,
    })


@login_required(login_url='login')
def buy_car(request, id):
    car = Car.objects.get(_id=ObjectId(id))

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.car = car
            if request.user.is_authenticated:
                order.user = request.user
            order.save()
            return redirect('car_detail', id=car.mongo_id)
    else:
        form = OrderForm()

    return render(request, 'cars/buy_car.html', {'form': form, 'car': car})

@login_required(login_url='login')
def make_offer(request, id):
    car = Car.objects.get(_id=ObjectId(id))

    if request.method == 'POST':
        form = OfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.car = car
            if request.user.is_authenticated:
                offer.user = request.user
            offer.save()
            return redirect('car_detail', id=car.mongo_id)
    else:
        form = OfferForm()

    return render(request, 'cars/make_offer.html', {'form': form, 'car': car})




def reviews_page(request):
    # Base queryset: all reviews
    all_reviews_qs = Review.objects.all()

    # --- Filtering by rating ---
    rating_filter = request.GET.get('rating', 'all')
    if rating_filter == '5':
        all_reviews_qs = all_reviews_qs.filter(rating=5)
    elif rating_filter == '4plus':
        all_reviews_qs = all_reviews_qs.filter(rating__gte=4)
    elif rating_filter == '3plus':
        all_reviews_qs = all_reviews_qs.filter(rating__gte=3)
    # else -> "all": no filter

    # --- Sorting ---
    sort = request.GET.get('sort', 'newest')
    if sort == 'oldest':
        all_reviews_qs = all_reviews_qs.order_by('created_at')
    elif sort == 'rating_high':
        all_reviews_qs = all_reviews_qs.order_by('-rating', '-created_at')
    elif sort == 'rating_low':
        all_reviews_qs = all_reviews_qs.order_by('rating', '-created_at')
    else:  # newest
        all_reviews_qs = all_reviews_qs.order_by('-created_at')

    # --- Pagination ---
    paginator = Paginator(all_reviews_qs, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Latest 4 reviews for the right preview list
    latest_reviews = Review.objects.order_by('-created_at')[:4]

    # --- Handle POST (new review submission) ---
    if request.method == 'POST':
        # If user not logged in → redirect to login
        if not request.user.is_authenticated:
            # redirect to login and return back after login
            login_url = reverse('login')
            next_url = reverse('reviews')
            return redirect(f"{login_url}?next={next_url}")

        # User is logged in → process form
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.save()
            return redirect('reviews')

    else:
        form = ReviewForm()

    # Render template
    return render(request, 'cars/reviews.html', {
        'form': form,
        'reviews': latest_reviews,
        'page_obj': page_obj,
        'current_sort': sort,
        'current_rating_filter': rating_filter,
    })




@login_required(login_url='login')
def appointment_page(request):
    submitted = False

    # Optional: car id from query parameter (?car=<mongo_id>)
    car_id = request.GET.get('car')
    initial = {}

    if car_id:
        try:
            car = Car.objects.get(_id=ObjectId(car_id))
            car_label = f"{car.make} {car.model} ({car.year})"
            initial['car_interest'] = car_label
        except Car.DoesNotExist:
            pass

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            if request.user.is_authenticated:
                appointment.user = request.user
            appointment.save()
            submitted = True
            # clear form after submit but keep same car preselected if present
            form = AppointmentForm(initial=initial)
    else:
        form = AppointmentForm(initial=initial)

    return render(request, 'cars/appointments.html', {
        'form': form,
        'submitted': submitted,
    })

@login_required
def my_activity(request):
    # Get objects linked to this user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    offers = Offer.objects.filter(user=request.user).order_by('-created_at')
    appointments = Appointment.objects.filter(user=request.user).order_by('-preferred_date')
    reviews = Review.objects.filter(user=request.user).order_by('-created_at')

    context = {
        'orders': orders,
        'offers': offers,
        'appointments': appointments,
        'reviews': reviews,
    }
    return render(request, 'cars/my_activity.html', context)

@login_required(login_url='login')
def edit_review(request, review_id):
    oid = mongo_pk_or_404(review_id)
    review = get_object_or_404(Review, pk=oid)

    # Only allow owner if user is set
    if review.user and review.user != request.user:
        return HttpResponseForbidden("You are not allowed to edit this review.")

    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "Your review has been updated.")
            return redirect('my_activity')
    else:
        form = ReviewForm(instance=review)

    return render(request, 'cars/edit_review.html', {'form': form, 'review': review})


@login_required(login_url='login')
def delete_order(request, order_id):
    oid = mongo_pk_or_404(order_id)
    order = get_object_or_404(Order, pk=oid)

    # If the order is linked to a user, enforce ownership
    if order.user and order.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this purchase request.")

    if request.method == 'POST':
        order.delete()
        messages.success(request, "Your purchase request has been removed.")
        return redirect('my_activity')

    return render(request, 'cars/confirm_delete.html', {
        'object': order,
        'type': 'purchase request',
        'cancel_url': reverse('my_activity'),
    })


@login_required(login_url='login')
def delete_offer(request, offer_id):
    oid = mongo_pk_or_404(offer_id)
    offer = get_object_or_404(Offer, pk=oid)

    if offer.user and offer.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this offer.")

    if request.method == 'POST':
        offer.delete()
        messages.success(request, "Your offer has been removed.")
        return redirect('my_activity')

    return render(request, 'cars/confirm_delete.html', {
        'object': offer,
        'type': 'offer',
        'cancel_url': reverse('my_activity'),
    })



@login_required(login_url='login')
def delete_appointment(request, appointment_id):
    oid = mongo_pk_or_404(appointment_id)
    appointment = get_object_or_404(Appointment, pk=oid)

    if appointment.user and appointment.user != request.user:
        return HttpResponseForbidden("You are not allowed to cancel this appointment.")

    if request.method == 'POST':
        appointment.delete()
        messages.success(request, "Your test-drive appointment has been cancelled.")
        return redirect('my_activity')

    return render(request, 'cars/confirm_delete.html', {
        'object': appointment,
        'type': 'test-drive appointment',
        'cancel_url': reverse('my_activity'),
    })



@login_required(login_url='login')
def delete_review(request, review_id):
    oid = mongo_pk_or_404(review_id)
    review = get_object_or_404(Review, pk=oid)

    if review.user and review.user != request.user:
        return HttpResponseForbidden("You are not allowed to delete this review.")

    if request.method == 'POST':
        review.delete()
        messages.success(request, "Your review has been deleted.")
        return redirect('my_activity')

    return render(request, 'cars/confirm_delete.html', {
        'object': review,
        'type': 'review',
        'cancel_url': reverse('my_activity'),
    })

@login_required(login_url='login')
def account_settings(request):
    """
    Let the logged-in user update their basic account information.
    """
    if request.method == "POST":
        form = UserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your account details have been updated.")
            return redirect("account_settings")
    else:
        form = UserUpdateForm(instance=request.user)

    return render(request, "cars/account_settings.html", {"form": form})


from django.shortcuts import render
from .models import Car


def car_list(request):
    # ---------- helper: safe numeric conversions ----------
    def to_float(value):
        """
        Convert price to float safely.
        Handles Decimal, int, '28900', '28,900', '$28900.00', etc.
        Returns None if it cannot be parsed.
        """
        if value is None:
            return None
        try:
            s = str(value)
            s = s.replace(',', '').replace('$', '').strip()
            if s == '':
                return None
            return float(s)
        except (ValueError, TypeError):
            return None

    def year_key(car):
        """
        Year as int (or 0 if missing/invalid) used for sorting.
        """
        try:
            return int(car.year)
        except (ValueError, TypeError):
            return 0

    def price_key(car):
        """
        Price as float (or 0 if missing/invalid) used for sorting.
        """
        val = to_float(car.price)
        return val if val is not None else 0.0

    # ---------- load all cars once as a Python list ----------
    cars = list(Car.objects.all())

    # ---------- SEARCH ----------
    search = (request.GET.get('search') or '').strip().lower()
    if search:
        cars = [
            c for c in cars
            if search in (c.make or '').lower()
            or search in (c.model or '').lower()
        ]

    # ---------- MIN PRICE ----------
    min_price_raw = (request.GET.get('min_price') or '').strip()
    if min_price_raw:
        try:
            min_price_val = float(min_price_raw)
            cars = [
                c for c in cars
                if (
                    to_float(c.price) is not None
                    and to_float(c.price) >= min_price_val
                )
            ]
        except ValueError:
            # ignore invalid min_price input
            pass

    # ---------- MAX PRICE ----------
    max_price_raw = (request.GET.get('max_price') or '').strip()
    if max_price_raw:
        try:
            max_price_val = float(max_price_raw)
            cars = [
                c for c in cars
                if (
                    to_float(c.price) is not None
                    and to_float(c.price) <= max_price_val
                )
            ]
        except ValueError:
            # ignore invalid max_price input
            pass

    # ---------- SORTING ----------
    sort = (request.GET.get('sort') or '').strip()

    if sort == 'price_asc':
        cars = sorted(cars, key=price_key)
    elif sort == 'price_desc':
        cars = sorted(cars, key=price_key, reverse=True)
    elif sort == 'year_new':
        cars = sorted(cars, key=year_key, reverse=True)
    elif sort == 'year_old':
        cars = sorted(cars, key=year_key)
    else:
        # default: newest year first, then cheaper price
        cars = sorted(cars, key=lambda c: (-year_key(c), price_key(c)))

    return render(request, 'cars/car_list.html', {'cars': cars})
