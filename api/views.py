"""
Views for Inventory Management System with query parameter filtering.

This module defines:
- `UserViewSet`: Provides CRUD endpoints for the Django `User` model.
- `InventoryViewSet`: Provides CRUD endpoints for the `Inventory` model with optional filtering by `user_id`.
- `InventoryItemViewSet`: Provides CRUD endpoints for the `InventoryItem` model with optional filtering by `inventory_id`.

These viewsets use Django REST Framework's `ModelViewSet` to automatically provide `list`, `create`, `retrieve`,
`update`, and `destroy` actions. Filtering is implemented by overriding `get_queryset`.
"""

import logging

from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from requests_oauthlib import OAuth1Session
from rest_framework import viewsets, status
from rest_framework.exceptions import PermissionDenied
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.models import Token

from .models import Inventory, InventoryItem
from .permissions import IsStaffUser
from .serializers import (
    UserSerializer,
    InventorySerializer,
    InventoryItemSerializer
)

logger = logging.getLogger("django.main.logger")


def permission_denied_view(request):
    """Site rendering the information about no required permissions."""
    return render(request, 'api/permission_denied.html', status=403)


def is_user_staff(user):
    # return user.is_staff
    return True  # For testing purposes, always return True
    # This is only for VIEWS, API permissions are handled in api/permissions.py


PERMISSION_DENIED_REDIRECT_URL = '/permission-denied/'
USOS_REQUEST_TOKEN_URL = 'https://apps.usos.pw.edu.pl/services/oauth/request_token'
USOS_AUTHORIZE_URL = 'https://apps.usos.pw.edu.pl/services/oauth/authorize'
USOS_ACCESS_TOKEN_URL = 'https://apps.usos.pw.edu.pl/services/oauth/access_token'


class UserStatusView(APIView):
    """
    An endpoint to check if a user is currently authenticated.
    If authenticated, returns the user's data.
    If not, the permission class will return a 401 Unauthorized.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)


class OAuthLoginView(APIView):
    """
    Initiates the USOS OAuth process.
    Creates an OAuth1 session, obtains a request token, stores it in the session,
    and then redirects the user to USOS's authorization URL.
    """

    def get(self, request, format=None):
        consumer_key = settings.USOS_CONSUMER_KEY
        consumer_secret = settings.USOS_CONSUMER_SECRET

        # Pobierz parametr 'source' z zapytania
        source = request.query_params.get('source', 'web')

        # Build the absolute callback URL dynamically.
        callback_uri = request.build_absolute_uri(f'/oauth/callback/?source={source}')
        oauth = OAuth1Session(consumer_key, client_secret=consumer_secret, callback_uri=callback_uri)

        # Step 1: Obtain an unauthorized Request Token.
        fetch_response = oauth.fetch_request_token(USOS_REQUEST_TOKEN_URL)
        request.session['resource_owner_key'] = fetch_response.get('oauth_token')
        request.session['resource_owner_secret'] = fetch_response.get('oauth_token_secret')

        # Step 2: Redirect the user to USOS's authorization URL.
        # zmiana na confirm_user -> da sie wylogowac ale dziwne
        authorization_url = oauth.authorization_url(USOS_AUTHORIZE_URL, interactivity='confirm_user')
        return redirect(authorization_url)


class OAuthCallbackView(APIView):
    """
    Handles the callback from USOS.
    Retrieves the oauth_verifier and the request token from the session,
    exchanges them for an access token, and then logs in or creates a Django user.
    For demonstration purposes, this view returns the access token details.
    """

    def get(self, request, format=None):
        consumer_key = settings.USOS_CONSUMER_KEY
        consumer_secret = settings.USOS_CONSUMER_SECRET

        resource_owner_key = request.session.get('resource_owner_key')
        resource_owner_secret = request.session.get('resource_owner_secret')
        oauth_verifier = request.query_params.get('oauth_verifier')

        if not resource_owner_key or not resource_owner_secret or not oauth_verifier:
            logger.warning("OAuthCallbackView: Missing token or verifier in session or callback parameters.")
            return Response({'error': 'Missing token or verifier in session or callback parameters.'}, status=400)

        # Create a new OAuth1 session with the verifier to get the access token.
        oauth_usos_session = OAuth1Session(
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=resource_owner_key,
            resource_owner_secret=resource_owner_secret,
            verifier=oauth_verifier
        )

        try:
            oauth_tokens = oauth_usos_session.fetch_access_token(USOS_ACCESS_TOKEN_URL)
        except Exception as e:
            logger.error(f"OAuthCallbackView: Failed to fetch access token from USOS: {e}", exc_info=True)
            return Response({'error': f'Failed to fetch access token: {str(e)}'}, status=500)

        access_token = oauth_tokens.get('oauth_token')
        access_token_secret = oauth_tokens.get('oauth_token_secret')

        if not access_token or not access_token_secret:
            logger.error("OAuthCallbackView: Failed to obtain access token or secret from USOS response.")
            return Response({'error': 'Failed to obtain access token from USOS.'}, status=500)

        # Also stored in the session for later ease of use.
        # If not required those two lines can be later removed.
        request.session['access_token'] = access_token
        request.session['access_token_secret'] = access_token_secret

        user_api_client = OAuth1Session(  # New session with the received access token
            consumer_key,
            client_secret=consumer_secret,
            resource_owner_key=access_token,
            resource_owner_secret=access_token_secret
        )

        user_endpoint = 'https://apps.usos.pw.edu.pl/services/users/user'  # USOS API endpoint for user info

        # Fields to be retrieved from USOS API to fill the Django User model.
        usos_fields = [
            'id', 'first_name', 'last_name', 'student_status', 'staff_status', 'email', 'has_email', 'profile_url'
        ]
        params = {'fields': '|'.join(usos_fields)}

        try:
            response = user_api_client.get(user_endpoint, params=params)
            response.raise_for_status()
            user_info = response.json()
        except Exception as e:
            logger.error(f"OAuthCallbackView: Unable to retrieve user info from USOS: {e}", exc_info=True)
            request.session['user_info'] = {"error": f"Unable to retrieve user info from USOS: {str(e)}"}

            error_detail = {"error": "Unable to retrieve user info from USOS."}
            try:
                error_detail['usos_response'] = response.json()
            except:
                error_detail['usos_response_text'] = response.text
            return Response(error_detail, status=response.status_code if hasattr(response, 'status_code') else 500)

        # Save the retrieved info in the session for other views to use.
        request.session['user_info'] = user_info

        # Creating or updating the Django user.
        # We need to check if the user already exists in our database.
        usos_id = user_info.get('id')

        # Making sure the usos response contains the ID (is not corrupted or empty?)
        if not usos_id:
            logger.error("OAuthCallbackView: USOS ID not found in user_info response.")
            return Response({'error': 'Critical: USOS user ID not found in API response.'}, status=500)

        # Creating a unique username based on the USOS ID.
        username = f"usos_{str(usos_id)}"

        usos_staff_status = user_info.get('staff_status')  # Getting staff status from USOS
        # 0 - student, 1 - worker but not teacher, 2 - teacher

        is_staff_member = False # TO CHANGE, FOR TESTING PURPOSES
        if usos_staff_status == 1 or usos_staff_status == 2:
            is_staff_member = True

        user_defaults = {
            'first_name': user_info.get('first_name', ''),
            'last_name': user_info.get('last_name', ''),
            'email': user_info.get('email') or '',
            'is_active': True,  # Instant activation
            'is_staff': is_staff_member,
            # 'is_superuser' False by default
            # 'last_login' is set automatically by Django when the user logs in
            # 'date_joined' is set automatically by Django when the user is created
        }

        # Creating / Modifying the user in the database
        try:
            user, created = User.objects.get_or_create(
                username=username,
                defaults=user_defaults
            )

            if created:
                # unusable password since Authentication is externally done via OAuth
                user.set_unusable_password()
                user.save()
                logger.info(f"OAuthCallbackView: Created new user: {username}")
            else:
                # User already exists, update the fields if they differ
                update_fields_list = []
                for field_name, value in user_defaults.items():
                    if getattr(user, field_name) != value:
                        setattr(user, field_name, value)
                        update_fields_list.append(field_name)

                if not user.is_active:  # Make user active if not already
                    user.is_active = True
                    update_fields_list.append('is_active')

                if update_fields_list:  # Save the user only if there are changes
                    user.save(update_fields=update_fields_list)
                    logger.info(f"OAuthCallbackView: Updated existing user: {username}, fields: {update_fields_list}")
                else:
                    logger.info(f"OAuthCallbackView: User {username} already up-to-date.")

            # Log the user in
            login(request, user)
            logger.info(f"OAuthCallbackView: User {username} logged in successfully.")

            source = request.query_params.get('source')
            if source == 'mobile':
                token, _ = Token.objects.get_or_create(user=user)
                serializer = UserSerializer(user)
                response_data = serializer.data
                response_data['token'] = token.key
                return Response(response_data, status=status.HTTP_200_OK)
            elif source == 'backend_test': 
                # ZEBY WEJSC W TEGO IFA : http://api-inventario.dyplomy.iem.pw.edu.pl:8000/oauth/login/?source=backend_test
                
                # Przekierowanie na adres backendu dla celów testowych
                # Możesz użyć pełnej nazwy DNS dla backendu
                return redirect('http://api-inventario.dyplomy.iem.pw.edu.pl:8000/')
            else: # source == 'web' (domyślny)
                # Docelowe przekierowanie na adres frontendu
                # Upewnij się, że adres Twojej webówki jest poprawny
                return redirect('http://inventario.dyplomy.iem.pw.edu.pl') # Adres frontendu na porcie 3000 bez jawnego portu
            
            
        except Exception as e:
            logger.error(f"OAuthCallbackView: Database error during user provisioning for {username}: {e}",
                         exc_info=True)
            # Return a proper error response
            return Response({'error': f'Database error during user provisioning: {str(e)}'}, status=500)


class LogoutView(APIView):
    """
    Handles user logout by clearing session data and logging out the user.
    """
    permission_classes = [IsAuthenticated]

    def perform_logout(self, request):
        request.session.flush()
        logout(request)
        return Response({"message": "Successfully logged out."}, status=200)

    def post(self, request, format=None):
        return self.perform_logout(request)

    def get(self, request, format=None):
        # Not recommended, added just for backend testing - when connecting with frontend REMOVE
        # Send post request to logout instead 
        return self.perform_logout(request)


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
    permission_classes = [IsAuthenticated, IsStaffUser]
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
    permission_classes = [IsAuthenticated, IsStaffUser]
    serializer_class = InventorySerializer
    queryset = Inventory.objects.all()

    def get_queryset(self):
        """
        Returns a filtered queryset.
        Filters by the currently logged-in user if authenticated.
        If the user is not authenticated, returns an empty queryset.
        """
        queryset = super().get_queryset()

        if self.request.user.is_authenticated:
            queryset = queryset.filter(user=self.request.user)
        else:
            queryset = queryset.none()

        return queryset

    def perform_create(self, serializer):
        """
        This automatically sets the user to the request's user when creating a new inventory.
        """

        serializer.save(user=self.request.user)


class InventoryItemViewSet(viewsets.ModelViewSet):
    """
    Provides CRUD (Create, Read, Update, Delete) endpoints for the `InventoryItem` model.
    Users can only access items from their own inventories.
    Optional filtering by `inventory_id` (must belong to the authenticated user). For example:
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
    permission_classes = [IsAuthenticated, IsStaffUser]
    serializer_class = InventoryItemSerializer
    queryset = InventoryItem.objects.all()

    def get_queryset(self):
        """
        Returns a filtered queryset if `inventory_id` is present in the query parameters.
        Otherwise, returns all InventoryItem objects.
        """
        if not self.request.user.is_authenticated:
            return InventoryItem.objects.none()

        # Base queryset: only items from user's own inventories
        queryset = InventoryItem.objects.filter(inventory__user=self.request.user)
        inventory_id = self.request.query_params.get('inventory_id')

        if inventory_id is not None:
            queryset = queryset.filter(inventory__id=inventory_id)

        return queryset

    def create(self, request, *args, **kwargs):
        """
        Handles POST requests for creating InventoryItem objects.

        If a list of objects is provided, performs bulk creation.
        Otherwise, falls back to the default single-object creation behavior.

        Items can only be created in inventories owned by the current user.
        """
        data = request.data

        if isinstance(data, list):
            if not data:  # Handle empty list
                return Response([], status=status.HTTP_201_CREATED)

            serializer = self.get_serializer(data=data, many=True)
            serializer.is_valid(raise_exception=True)

            # Validate that all inventories belong to the current user
            for item_data in serializer.validated_data:
                inventory = item_data.get('inventory')
                if inventory and inventory.user != request.user:
                    return Response(
                        {'error': f'Cannot create item in inventory {inventory.id}: Permission denied'},
                        status=status.HTTP_403_FORBIDDEN
                    )

            self.perform_bulk_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        """
        Validates that the inventory belongs to the current user before creating the item.
        """
        inventory = serializer.validated_data.get('inventory')
        if inventory and inventory.user != self.request.user:
            raise PermissionDenied('Cannot create item in inventory that does not belong to you')
        serializer.save()

    def perform_bulk_create(self, serializer):
        """
        Saves multiple InventoryItem objects using the validated serializer.
        This method is called internally by `create()` when a list of items is posted.
        """
        serializer.save()
