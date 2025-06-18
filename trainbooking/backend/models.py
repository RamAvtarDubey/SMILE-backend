from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# Create your models here.

class Train(models.Model):
    name = models.CharField(max_length=100)
    source = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)

    departure_time = models.DateTimeField(default=timezone.now)

    total_seats = models.IntegerField()
    seats_available = models.IntegerField()

    def __str__(self):
        return self.name
    


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    train = models.ForeignKey(Train, on_delete=models.CASCADE)
    seat_number = models.IntegerField()
    booking_time = models.DateTimeField(default=timezone.now)
    
    def __self__(self):
        return self.user