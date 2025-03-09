"""
Views for Inventory Management System with query parameter filtering.

This module defines:
- `UserViewSet`: Provides CRUD endpoints for the Django `User` model.
- `InventoryViewSet`: Provides CRUD endpoints for the `Inventory` model with optional filtering by `user_id`.
- `InventoryItemViewSet`: Provides CRUD endpoints for the `InventoryItem` model with optional filtering by `inventory_id`.

These viewsets use Django REST Framework's `ModelViewSet` to automatically provide `list`, `create`, `retrieve`,
`update`, and `destroy` actions. Filtering is implemented by overriding `get_queryset`.
"""

from django.contrib.auth.models import User
from rest_framework import viewsets

from .models import Inventory, InventoryItem
from .serializers import (
    UserSerializer,
    InventorySerializer,
    InventoryItemSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD (Create, Read, Update, Delete) endpoints for the Django `User` model.

    Auto-generated Fields:
        - `id` (int): Automatically created primary key.

    Included Fields:
        - `username` (str): Unique identifier for the user.
        - `email` (str): Email address of the user.
        - `inventories` (list[int]): IDs of associated inventories (read-only).

    Endpoints:
        - List all users (GET):       `/users/`
        - Create a new user (POST):   `/users/`
        - Retrieve a user (GET):      `/users/{id}/`
        - Update a user (PUT/PATCH):  `/users/{id}/`
        - Delete a user (DELETE):     `/users/{id}/`
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class InventoryViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD (Create, Read, Update, Delete) endpoints for the `Inventory` model,
    with optional filtering by user_id. For example:
        GET /inventories/?user_id=5
    returns only inventories owned by the user with ID=5.

    Auto-generated Fields:
        - `id` (int): Automatically created primary key.

    Included Fields:
        - `name` (str): Name of the inventory.
        - `date` (date): Creation date.
        - `user` (nested `UserSerializer`): Owner of this inventory (read-only).
        - `items` (list[int]): IDs of related `InventoryItem` objects.

    Endpoints:
        - List all inventories (GET):       `/inventories/`
        - Create a new inventory (POST):    `/inventories/`
        - Retrieve an inventory (GET):      `/inventories/{id}/`
        - Update an inventory (PUT/PATCH):  `/inventories/{id}/`
        - Delete an inventory (DELETE):     `/inventories/{id}/`
    """
    serializer_class = InventorySerializer
    queryset = Inventory.objects.all()

    def get_queryset(self):
        """
        Returns a filtered queryset if `user_id` is present in the query parameters.
        Otherwise, returns all Inventory objects.
        """
        queryset = super().get_queryset()
        user_id = self.request.query_params.get('user_id')
        if user_id is not None:
            queryset = queryset.filter(user__id=user_id)
        return queryset

    def perform_create(self, serializer):
        """
        This automatically sets the user to the request's user when creating a new inventory.
        """

        serializer.save(user=self.request.user)


class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD (Create, Read, Update, Delete) endpoints for the `InventoryItem` model,
    with optional filtering by `inventory_id`. For example:
        GET /items/?inventory_id=10
    returns only items belonging to the inventory with ID=10.

    Auto-generated Fields:
        - `id` (int): Automatically created primary key.

    Included Fields:
        - `inventory` (int): ID of the associated `Inventory`.
        - `department` (int): Department number.
        - `asset_group` (int): Asset group.
        - `category` (str): Category name.
        - `inventory_number` (str): Unique inventory number.
        - `asset_component` (int): Asset component ID.
        - `sub_number` (int): Sub-number for the asset.
        - `acquisition_date` (date): Acquisition date.
        - `asset_description` (str): Description of the asset.
        - `quantity` (int): Number of items.
        - `initial_value` (decimal): Initial monetary value.
        - `lastInventoryRoom` (str): Room location during last inventory.
        - `currentRoom` (str): Current room location.

    Endpoints:
        - List all items (GET):             `/items/`
        - Create a new item (POST):         `/items/`
        - Retrieve an item (GET):           `/items/{id}/`
        - Update an item (PUT/PATCH):       `/items/{id}/`
        - Delete an item (DELETE):          `/items/{id}/`
    """
    serializer_class = InventoryItemSerializer
    queryset = InventoryItem.objects.all()

    def get_queryset(self):
        """
        Returns a filtered queryset if `inventory_id` is present in the query parameters.
        Otherwise, returns all InventoryItem objects.
        """
        queryset = super().get_queryset()
        inventory_id = self.request.query_params.get('inventory_id')
        if inventory_id is not None:
            queryset = queryset.filter(inventory__id=inventory_id)
        return queryset
