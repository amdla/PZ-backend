"""
Serializers for Inventory Management System.

This module defines:
- `UserSerializer`: Serializes Django's built-in User model.
- `InventorySerializer`: Serializes Inventory model.
- `InventoryItemSerializer`: Serializes InventoryItem model.

Django's built-in `User` model contains:
- `id` (int, auto-generated primary key)
- `username` (str, unique identifier)
- `email` (str, optional field)
- Other fields like `password`, `first_name`, and `last_name` (not included here).
"""

from django.contrib.auth.models import User  # Django's built-in auth user
from rest_framework import serializers

from models import Inventory, InventoryItem


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for Django's built-in User model.

    Auto-generated Fields:
        - `id` (int): Automatically created by Django.

    Included Fields:
        - `username` (str): Unique identifier for the user.
        - `email` (str): Email of the user (can be optional).
        - `inventories` (list of int): IDs of inventories owned by the user.

    Relationships:
        - `inventories`: Lists all inventory IDs associated with the user.
    """

    inventories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'inventories']


class InventorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Inventory model.

    Auto-generated Fields:
        - `id` (int): Automatically created by Django.

    Included Fields:
        - `name` (str): Name of the inventory.
        - `date` (date): Creation date.
        - `user` (nested UserSerializer): User who owns this inventory.
        - `items` (list of int): IDs of inventory items in this inventory.

    Relationships:
        - `user`: Read-only nested representation of the user.
        - `items`: List of inventory item IDs related to this inventory.
    """

    user = UserSerializer(read_only=True)
    items = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = Inventory
        fields = ['id', 'name', 'date', 'user', 'items']


class InventoryItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the InventoryItem model.

    Auto-generated Fields:
        - `id` (int): Automatically created by Django.

    Included Fields:
        - `inventory` (int): ID of the related inventory.
        - `department` (int): Department number.
        - `asset_group` (int): Asset group.
        - `category` (str): Category name.
        - `inventory_number` (str): Unique inventory number.
        - `asset_component` (int): Asset component ID.
        - `sub_number` (int): Sub-number.
        - `acquisition_date` (date): Acquisition date.
        - `asset_description` (str): Description of the asset.
        - `quantity` (int): Number of items.
        - `initial_value` (decimal): Initial monetary value.
        - `room` (str): Room location.

    Relationships:
        - `inventory`: Linked by `ForeignKey(Inventory)`, allowing selection by ID.
    """

    inventory = serializers.PrimaryKeyRelatedField(queryset=Inventory.objects.all())

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'inventory', 'department', 'asset_group', 'category',
            'inventory_number', 'asset_component', 'sub_number', 'acquisition_date',
            'asset_description', 'quantity', 'initial_value', 'room'
        ]
