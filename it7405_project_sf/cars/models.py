from djongo import models
from django.contrib.auth.models import User

class Car(models.Model):
    _id = models.ObjectIdField()
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image_url = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"

    @property
    def mongo_id(self):
        return str(self._id)


class Car(models.Model):
    _id = models.ObjectIdField()
    make = models.CharField(max_length=100)
    model = models.CharField(max_length=100)
    year = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    image_url = models.CharField(max_length=300)

    def __str__(self):
        return f"{self.make} {self.model} ({self.year})"

    @property
    def mongo_id(self):
        return str(self._id)


class Order(models.Model):
    _id = models.ObjectIdField()
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order for {self.car} by {self.full_name}"


class Offer(models.Model):
    _id = models.ObjectIdField()
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
        ],
        default='pending',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Offer {self.amount} on {self.car}"

# ... your existing Car, Order, Offer models ...

class Review(models.Model):
    _id = models.ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    rating = models.IntegerField(
        choices=[(1, '1 - Very poor'),
                 (2, '2 - Poor'),
                 (3, '3 - Average'),
                 (4, '4 - Good'),
                 (5, '5 - Excellent')]
    )
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.full_name} ({self.rating}/5)"


class Appointment(models.Model):
    _id = models.ObjectIdField()
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=30)
    car_interest = models.CharField(max_length=150, help_text="Car you want to test drive")
    preferred_date = models.DateField()
    preferred_time = models.CharField(
        max_length=20,
        choices=[
            ('morning', 'Morning'),
            ('afternoon', 'Afternoon'),
            ('evening', 'Evening'),
        ]
    )
    message = models.TextField(blank=True)

    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('confirmed', 'Confirmed'),
            ('cancelled', 'Cancelled'),
        ],
        default='pending'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Appointment for {self.full_name} on {self.preferred_date}"
