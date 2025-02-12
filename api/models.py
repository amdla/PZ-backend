from django.db import models
from django.contrib.auth.models import User

class Inventory(models.Model):
    inventory_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=255)
    date = models.DateField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.inventory_number} - {self.name}"

class InventoryItem(models.Model):
    inventory = models.ForeignKey(Inventory, on_delete=models.CASCADE, related_name="items")
    department = models.IntegerField()  # "Dział gospodarczy"
    asset_group = models.IntegerField()  # "Grupa aktywów trw."
    category = models.CharField(max_length=50)  # "Grupa rodzajowa"
    inventory_number = models.CharField(max_length=50)
    asset_component = models.BigIntegerField()  # "Składnik aktyw. trw."
    sub_number = models.IntegerField()
    acquisition_date = models.DateField()
    asset_description = models.CharField(max_length=255)  # "Oznaczenie aktywów trwałych"
    quantity = models.IntegerField()
    initial_value = models.DecimalField(max_digits=10, decimal_places=2)  # "WartPocz"
    room = models.CharField(max_length=50)  # "Pomieszczenie"

    def __str__(self):
        return f"{self.inventory_number} - {self.asset_description}"
