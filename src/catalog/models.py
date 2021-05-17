from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from PIL import Image

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=9, decimal_places=2)
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    active = models.BooleanField(default=True)
    photo = models.ImageField(upload_to='items/', default='items/default.png')

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        """Returns the url to access a detail record for this item."""
        return reverse('catalog:item-detail', args=[str(self.id)])

class Category(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name 

    class Meta:
        verbose_name_plural = "categories"


class OrderItem(models.Model):
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    date_added = models.DateTimeField(auto_now=True)

    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name="orderitems", blank=True, null=True)

    def __str__(self):
        return self.item.name

    def get_total_item_price(self):
        return self.item.price * self.quantity 

    
class Order(models.Model):
    PICKUP_TIME_SLOT_CHOICES = [
        ('m', 'Morning (9AM - 11AM'),
        ('n', 'Midday (12PM - 2PM)'),
        ('e', 'Evening (4PM - 6PM'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField(blank=True, null=True)
    ordered = models.BooleanField(default=False)
    fulfilled = models.BooleanField(default=False)
    payment_id = models.CharField(max_length=100, null=True, blank=True)
    pickup_time_slot = models.CharField(
        max_length=1,
        choices=PICKUP_TIME_SLOT_CHOICES,
        blank=True,
        default='m',
        )

    def __str__(self):
        return f"{self.user.username}'s order - Order ID {self.id}"

    def get_total(self):
        total = 0
        for item in self.orderitems.all():
            total += item.get_total_item_price()
        return total 
    