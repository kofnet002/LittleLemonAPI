from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, UserSerializer, CartSerializer, OrderSerializer, OrderItemSerializer
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.test import Client


# Create your views here.
class MenuItemView(APIView):
    def get(self, request):
        menu_items = MenuItem.objects.all()
        serializer = MenuItemSerializer(menu_items, many=True)
        if request.user.has_perm('LittleLemonAPI.view_menuitem'):
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Not authorized to view this page", status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        if request.user.groups.filter(name="Manager"):
            data = MenuItemSerializer(data=request.data)
            if data.is_valid():
                data.save()
                return Response(data.data, status=status.HTTP_201_CREATED)
            else:
                return Response(data.errors, status=status.HTTP_403_FORBIDDEN)
        return Response("Not authorized...", status=status.HTTP_403_FORBIDDEN)


class MenuItemDetail(APIView):
    def get_object(self, id):
        try:
            return MenuItem.objects.get(id=id)
        except MenuItem.DoesNotExist:
            pass
    
    def get(self, request, id):
        menu_item = MenuItemSerializer(self.get_object(id))
        return Response(menu_item.data, status=status.HTTP_200_OK)

    def put(self, request, id):
        menu_item = self.get_object(id)
        data = MenuItemSerializer(menu_item, data=request.data)
        if request.user.groups.filter(name="Manager"):
            if data.is_valid():
                data.save()
                return Response(data.data, status=status.HTTP_201_CREATED)
        return Response("Not authorised to make changes", status=status.HTTP_403_FORBIDDEN)

    def delete(self, request, id):
        menu_item = self.get_object(id)
        if request.user.groups.filter(name="Manager"):
            menu_item.delete()
            return Response("Deleted Successfully", status=status.HTTP_204_NO_CONTENT)
        return Response("Not authorised to remove item", status=status.HTTP_403_FORBIDDEN)


class UserGroupManagement(APIView):
    def get(self, request):
        users = User.objects.filter(groups__name="Manager")
        users_data = UserSerializer(users, many=True)
        if request.user.groups.filter(name="Manager"):
            return Response(users_data.data)
        return Response("Not authorized to view this page", status=status.HTTP_401_UNAUTHORIZED)

#    Assigns the user in the payload to the manager group and returns 201-Created
    def post(self, request, format=None):
        if request.user.groups.filter(name="Manager"):
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                manager_group = Group.objects.get(name='Manager')
                manager_group.user_set.add(user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("Not authorized...", status=status.HTTP_401_UNAUTHORIZED)


class RemoveUserFromManagerGroup(APIView):
    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        group = Group.objects.get(name='Manager')
        if request.user.groups.filter(name="Manager"):
            if group in user.groups.all():
                user.groups.remove(group)
                return Response("User removed successfully!", status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User is not a member of the manager group'}, status=status.HTTP_400_BAD_REQUEST)
        return Response("Not authorized", status=status.HTTP_401_UNAUTHORIZED)


class DeliveryCrewManagerGroup(APIView):
    def get(self, request):
        users = User.objects.filter(groups__name="Delivery crew")
        users_data = UserSerializer(users, many=True)
        if request.user.groups.filter(name="Manager"):
            return Response(users_data.data)
        return Response("Not authorized to view this page", status=status.HTTP_401_UNAUTHORIZED)
    
    def post(self, request, format=None):
        if request.user.groups.filter(name="Manager"):
            serializer = UserSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                manager_group = Group.objects.get_or_create(name='Delivery crew')
                manager_group.user_set.add(user)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("Not authorized...", status=status.HTTP_401_UNAUTHORIZED)


class RemoveUserFromDeliveryCrewGroup(APIView):
    def delete(self, request, id):
        try:
            user = User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)

        group = Group.objects.get(name='Delivery crew')
        if request.user.groups.filter(name="Manager"):
            if group in user.groups.all():
                user.groups.remove(group)
                return Response("User removed successfully!", status=status.HTTP_200_OK)
            else:
                return Response({'error': 'User is not a member of the manager group'}, status=status.HTTP_400_BAD_REQUEST)
        return Response("Not authorized", status=status.HTTP_401_UNAUTHORIZED)


class CartView(APIView):
    def get(self, request):
        user = request.user
        carts = Cart.objects.filter(user=user)  
        serializer = CartSerializer(carts, many=True)
        if request.user.groups.filter(name="customer"):
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response("Not authorized to view this page", status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        if request.user.groups.filter(name="customer"):
            serializer = CartSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("Not authorized...", status=status.HTTP_400_BAD_REQUEST)


class RemoveCartItem(APIView):
    def get_object(self, id):
        try:
            return Cart.objects.get(id=id)
        except Cart.DoesNotExist:
            return Response("Cart object not found", status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, id):
        if request.user.groups.filter(name="customer"):
            cart = self.get_object(id)
            if cart.user == request.user:
                cart.delete()
                return Response("Cart deleted successfully!", status=status.HTTP_404_NOT_FOUND)
            return Response("Not authorized to delete", status=status.HTTP_401_UNAUTHORIZED)
        return Response("Not authorized to remove cart!", status=status.HTTP_401_UNAUTHORIZED)


class OrderView(APIView):
    def get(self, request):
        user = request.user
        orders = Order.objects.filter(user=user)
        serializer = OrderSerializer(orders, many=True)

        if request.user.groups.filter(name="customer"):
            return Response(serializer.data, status=status.HTTP_200_OK)
            
        elif request.user.groups.filter(name="Manager"):
            all_orders = OrderItem.objects.all()
            all_orders_serializer = OrderItemSerializer(all_orders, many=True)
            return Response(all_orders_serializer.data, status=status.HTTP_200_OK)
        
        elif request.user.groups.filter(name="Delivery crew"):
            # Get all orders with order items assigned to the delivery crew
            orders = Order.objects.filter(delivery_crew=request.user)
            # Serialize the orders and return them in a response object
            serializer = OrderSerializer(orders, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response("Not authorized...", status=status.HTTP_401_UNAUTHORIZED)

    def post(self, request):
        if request.user.group.filter(name="customer"):
            user = request.user
            # Get the cart items for the current user
            cart_items = Cart.objects.filter(user=user)

            # Create a new order item for each cart item
            for item in cart_items:
                order_item = OrderItem.objects.create(
                order=request.user,
                menuitem=item.menuitem,
                quantity=item.quantity,
                unit_price=item.unit_price,
                price=item.price,
            )

            # Delete all the cart items for the current user
            # client = Client()
            # response = client.delete('/api/cart/menu-items')
            cart_items.delete()
            return Response({"message": "Order items created and cart items deleted successfully."}, status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_401_UNAUTHORIZED)


class OrderDetail(APIView):
    def get_object(self, id):
        try:
            return Order.objects.get(id=id)
        except Order.DoesNotExist:
            pass
            # return Response('Order object not found', status=status.HTTP_404_NOT_FOUND)

    def get(self, request, id):
        order_item = OrderSerializer(self.get_object(id))
        # user = order_item.data.get('user').get('username')
        # if request.user.username == user and request.user.groups.filter(name="customer"):
        if request.user.groups.filter(name="customer"):
            return Response(order_item.data, status=status.HTTP_200_OK)
        else:
            return Response("Not authorized to view this page", status=status.HTTP_401_UNAUTHORIZED)
    
    def put(self, request, id):
        order_item = OrderSerializer(self.get_object(id))
        if request.user.groups.filter(name="customer" or "Manager"):
            serializer = OrderSerializer(order_item, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        elif request.user.groups.filter(name="Delivery crew"):
            order = OrderSerializer(order_item, data=request.data)
            if order.is_valid():
                order.save()
                return Response("Updated successfully", status=status.HTTP_201_CREATED)
            return Response(order.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response("Not authorized", status=status.HTTP_401_UNAUTHORIZED)
        
    def delete(self, request, id):
        if request.user.groups.filter(name="Manager"):
            order_item = self.get_object(id)
            order_item.delete()
            return Response("Deleted successfully!", status=status.HTTP_404_NOT_FOUND)
        return Response("Not authorized to remove this order", status=status.HTTP_401_UNAUTHORIZED)