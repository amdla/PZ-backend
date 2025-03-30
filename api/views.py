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

from django.conf import settings
from django.shortcuts import redirect
from rest_framework.views import APIView, View
from rest_framework.response import Response
from requests_oauthlib import OAuth1Session
from django.http import HttpResponse


USOS_REQUEST_TOKEN_URL = 'https://apps.usos.pw.edu.pl/services/oauth/request_token'
USOS_AUTHORIZE_URL = 'https://apps.usos.pw.edu.pl/services/oauth/authorize'
USOS_ACCESS_TOKEN_URL = 'https://apps.usos.pw.edu.pl/services/oauth/access_token'

class OAuthLoginView(APIView):
    """
    Initiates the USOS OAuth process.
    Creates an OAuth1 session, obtains a request token, stores it in the session,
    and then redirects the user to USOS's authorization URL.
    """
    def get(self, request, format=None):
        consumer_key = settings.USOS_CONSUMER_KEY
        consumer_secret = settings.USOS_CONSUMER_SECRET

        # Build the absolute callback URL dynamically.
        callback_uri = request.build_absolute_uri('/oauth/callback/')
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri=callback_uri)
        
        # Step 1: Obtain an unauthorized Request Token.
        fetch_response = oauth.fetch_request_token(USOS_REQUEST_TOKEN_URL)
        request.session['resource_owner_key'] = fetch_response.get('oauth_token')
        request.session['resource_owner_secret'] = fetch_response.get('oauth_token_secret')
        
        # Step 2: Redirect the user to USOS's authorization URL.
        authorization_url = oauth.authorization_url(USOS_AUTHORIZE_URL, interactivity='minimal')
        return redirect(authorization_url)

class OAuthCallbackView(APIView):
    """
    Handles the callback from USOS.
    Retrieves the oauth_verifier and the request token from the session,
    exchanges them for an access token, and then (optionally) logs in or creates a Django user.
    For demonstration purposes, this view returns the access token details.
    """
    def get(self, request, format=None):
        consumer_key = settings.USOS_CONSUMER_KEY
        consumer_secret = settings.USOS_CONSUMER_SECRET
        
        resource_owner_key = request.session.get('resource_owner_key')
        resource_owner_secret = request.session.get('resource_owner_secret')
        oauth_verifier = request.query_params.get('oauth_verifier')
        
        if not resource_owner_key or not resource_owner_secret or not oauth_verifier:
            return Response({'error': 'Missing token or verifier in session or callback parameters.'}, status=400)
        
        # Create a new OAuth1 session with the verifier to get the access token.
        oauth = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=oauth_verifier
        )
        oauth_tokens = oauth.fetch_access_token(USOS_ACCESS_TOKEN_URL)
        access_token = oauth_tokens.get('oauth_token')
        access_token_secret = oauth_tokens.get('oauth_token_secret')
        
        # Here, you might store the tokens in the user's session or in your database
        
        # Its so the user doesn't have to log in every time they access our app's API - JK
        # For now we store them in the session - JK
        request.session['access_token'] = access_token
        request.session['access_token_secret'] = access_token_secret

        # For demonstration we access the USOS API to get basic user data (name, surname) - JK
        user_endpoint = 'https://apps.usos.pw.edu.pl/services/users/user'
        params = {'fields': 'id|first_name|last_name'}
        response = oauth.get(user_endpoint, params=params)
        if response.status_code == 200:
            user_info = response.json()
        else:
            user_info = {"error": "Unable to retrieve user info."}
        
        # Save the retrieved info in the session.
        request.session['user_info'] = user_info
        # End of demonstration code - JK
        
        # Here you would normally create or update a Django user account 
        # ...

        # For now, we just redirect to the future dashboard - JK
        return redirect('/dashboard/')
    
class DashboardView(View):
    def get(self, request, *args, **kwargs):
        # Retrieve the stored user information from the session.
        user_info = request.session.get('user_info', {})
        # Display the info as a simple HTML response.
        return HttpResponse(f"<h1>Dashboard</h1><p>User Info: {user_info}</p>")
    

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
