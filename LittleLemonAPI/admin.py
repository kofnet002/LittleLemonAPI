from django.contrib import admin
from .models import Category, MenuItem, Cart, Order, OrderItem

# Register your models here.
admin.site.register([Category, MenuItem, Cart, Order, OrderItem])
