"""
URL Configuration for Inventory Management System.

This module defines URL patterns for CRUD operations on:
- User
- Inventory
- InventoryItem

`DefaultRouter` automatically generates the appropriate routes for each ModelViewSet.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from api.views import UserViewSet, InventoryViewSet, InventoryItemViewSet

# Create a router and register our viewsets.
router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')
router.register(r'inventories', InventoryViewSet, basename='inventory')
router.register(r'items', InventoryItemViewSet, basename='inventoryitem')

# The API URLs are now determined automatically by the router.
urlpatterns = [
    path('', include(router.urls)),
]
