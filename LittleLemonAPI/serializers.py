from rest_framework import serializers
from .models import MenuItem, Cart, Order, OrderItem
from django.contrib.auth.models import User

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = MenuItem
        fields = "__all__"
        depth = 1


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']


class CartSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    menuitem = MenuItemSerializer(read_only=True)
    class Meta:
        model = Cart
        fields = "__all__"


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)    
    delivery_crew = UserSerializer(read_only=True) 
    
    class Meta:
        model = Order
        fields = "__all__"
    
# data = OrderSerializer(User, many=True).data


class OrderItemSerializer(serializers.ModelSerializer):
    order = UserSerializer(read_only=True)    
    menuitem = MenuItemSerializer(read_only=True) 
    class Meta:
        model = OrderItem
        fields = "__all__"