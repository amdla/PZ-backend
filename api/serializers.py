from django.contrib.auth.models import User
from rest_framework import serializers

from models import Inventory, InventoryItem


class UserSerializer(serializers.ModelSerializer):
    inventories = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # Show user-owned inventories

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'inventories']


class InventorySerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)  # Nest user details
    items = serializers.PrimaryKeyRelatedField(many=True, read_only=True)  # List related inventory items

    class Meta:
        model = Inventory
        fields = ['id', 'name', 'date', 'user', 'items']


class InventoryItemSerializer(serializers.ModelSerializer):
    inventory = serializers.PrimaryKeyRelatedField(queryset=Inventory.objects.all())  # Allow selection by ID

    class Meta:
        model = InventoryItem
        fields = [
            'id', 'inventory', 'department', 'asset_group', 'category',
            'inventory_number', 'asset_component', 'sub_number', 'acquisition_date',
            'asset_description', 'quantity', 'initial_value', 'room'
        ]
