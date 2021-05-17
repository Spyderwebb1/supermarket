"""supermarket URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import path
from . import views

app_name = "catalog"

urlpatterns = [
    path('', views.home, name='home'),
    path('items/', views.items, name='items-list'),
    path('item/<int:pk>', views.item_detail, name='item-detail'),
    path('add-to-cart/<int:pk>', views.add_to_cart, name='add-to-cart'),
    path('update-cart-item/<int:pk>', views.update_cart_item, name='update-cart-item'),
    path('order-summary/', views.order_summary, name='order-summary'),
    path('category/<int:pk>', views.category_detail, name='category'),
    path('checkout/', views.checkout, name='checkout'),
    path('success/', views.success, name='success'),
    path('cancel/', views.cancel, name='cancel'),
    path('stripe-webhook/', views.stripe_webhook, name='stripe-webhook'),
]