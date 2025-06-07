"""
Models for Inventory Management System.

This module defines:
- `Inventory`: Represents an inventory owned by a Django user.
- `InventoryItem`: Represents individual items stored in an inventory.

Django's built-in `User` model is used to associate inventories with users.
Each model automatically includes an `id` field as a primary key.
"""

from django.contrib.auth.models import User
from django.db import models

class Inventory(models.Model):
    """
    Represents an inventory owned by a user.

    Auto-generated Fields:
        - `id` (int, primary key): Automatically created by Django.

    Fields:
        - `name` (str): Name of the inventory.
        - `date` (date): Date of inventory creation.
        - `user` (ForeignKey to User): The owner (linked to Django's built-in `User` model).

    Relationships:
        - Each inventory is linked to a user via `ForeignKey(User)`.
        - Related name for reverse lookup: `user.inventories.all()`.
    """

    name = models.CharField(max_length=255)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="inventories")  # Foreign Key to User

    def __str__(self):
        """
        Returns a readable string representation of the inventory.
        """
        return (f"Inventory id: {self.id},"
                f"Name: {self.name}, "
                f"Date: {self.date}, "
                f"User: {self.user.email}")


class InventoryItem(models.Model):
    """
    Represents an item stored within an inventory.

    Auto-generated Fields:
        - `id` (int, primary key): Automatically created by Django.

    Fields:
        - `inventory` (ForeignKey to Inventory): The associated inventory.
        - `department` (int): Department number.
        - `asset_group` (int): Asset group.
        - `category` (str): Category of the item.
        - `inventory_number` (str): Unique inventory number.
        - `asset_component` (int): Asset component ID.
        - `sub_number` (int): Sub-number of the asset.
        - `acquisition_date` (date): Date of acquisition.
        - `asset_description` (str): Description of the asset.
        - `quantity` (int): Number of units.
        - `initial_value` (decimal): Initial monetary value of the item.
        - `lastInventoryRoom` (str): Room where the item was previously stored.
        - `currentRoom` (str): Room where the item is stored at the moment.
        - `scanned` (boolean): Information whether the item has been scanned yet.

    Relationships:
        - Each item is linked to an inventory via `ForeignKey(Inventory)`.
        - Related name for reverse lookup: `inventory.items.all()`.
    """

    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="items")  # Foreign Key to Inventory
    department = models.IntegerField()  # Dział gospodarczy
    asset_group = models.IntegerField()  # Grupa aktywów trw.
    category = models.CharField(max_length=50)  # Grupa rodzajowa
    inventory_number = models.CharField(max_length=50)  # Numer inwentarzowy
    asset_component = models.BigIntegerField()  # Składnik aktyw. trw.
    sub_number = models.IntegerField()  # Podnumer
    acquisition_date = models.DateField()  # Pierwsza data
    asset_description = models.CharField(max_length=255)  # Oznaczenie aktywów trwałych
    quantity = models.IntegerField()  # "Ilość"
    initial_value = models.DecimalField(max_digits=10, decimal_places=2)  # Wartość
    lastInventoryRoom = models.CharField(max_length=50)  # Poprzednie pomieszczenie
    currentRoom = models.CharField(max_length=50,null=True,blank=True)  # Pomieszczenie
    scanned = models.BooleanField(null=True,blank=True)
    
    def __str__(self):
        """
        Returns a readable string representation of the inventory item.
        """
        return (f"Inventory item id: {self.id}, "
                f"Inventory number: {self.inventory.id}, "
                f"Department: {self.department}, "
                f"Asset group: {self.asset_group}, "
                f"Category: {self.category}, "
                f"Inventory number: {self.inventory_number}, "
                f"Asset component: {self.asset_component}, "
                f"Sub number: {self.sub_number}, "
                f"Acquisition date: {self.acquisition_date}, "
                f"Asset description: {self.asset_description}, "
                f"Quantity: {self.quantity}, "
                f"Initial value: {self.initial_value}, "
                f"Last Inv room: {self.lastInventoryRoom}"
                f"Current room: {self.currentRoom}"
                f"Scanned : {self.scanned}")
