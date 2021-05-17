from django.forms import ModelForm
from .models import Order

class PickUpForm(ModelForm):

   class Meta:
        model = Order
        fields = ('pickup_time_slot',)