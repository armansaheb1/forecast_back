import logging
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from django.shortcuts import get_object_or_404
from .models import FortuneProfile
from .serializers import FortuneProfileSerializer

logger = logging.getLogger('main')


class FortuneProfileViewSet(ModelViewSet):
    """
    ViewSet for managing fortune reading profiles.
    
    - List: GET /api/v1/profiles/ - Get all profiles for authenticated user (or empty if not authenticated)
    - Create: POST /api/v1/profiles/ - Create a new profile
    - Retrieve: GET /api/v1/profiles/{id}/ - Get a specific profile
    - Update: PUT/PATCH /api/v1/profiles/{id}/ - Update a profile
    - Delete: DELETE /api/v1/profiles/{id}/ - Delete a profile
    
    Authentication: Optional (profiles can be created without login, but login allows syncing)
    """
    serializer_class = FortuneProfileSerializer
    permission_classes = [permissions.AllowAny]  # Allow anonymous profiles
    
    def get_queryset(self):
        """
        Return profiles for authenticated user, or empty queryset for anonymous users.
        Anonymous users can still create profiles, but won't see them in list.
        """
        if self.request.user.is_authenticated:
            return FortuneProfile.objects.filter(user=self.request.user)
        return FortuneProfile.objects.none()
    
    def perform_create(self, serializer):
        """Assign profile to user if authenticated"""
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save()
        logger.info(f"Profile created: {serializer.instance.name}")
    
    def get_object(self):
        """Get profile, ensuring user can only access their own profiles if authenticated"""
        obj = get_object_or_404(FortuneProfile, pk=self.kwargs['pk'])
        
        # If user is authenticated, only allow access to their own profiles
        if self.request.user.is_authenticated:
            if obj.user != self.request.user:
                from rest_framework.exceptions import PermissionDenied
                raise PermissionDenied("You can only access your own profiles.")
        
        # If user is not authenticated, allow access to profiles without user
        elif obj.user is not None:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("This profile belongs to a user account.")
        
        return obj
    
    def destroy(self, request, *args, **kwargs):
        """Delete profile"""
        instance = self.get_object()
        self.perform_destroy(instance)
        logger.info(f"Profile deleted: {instance.name}")
        return Response(status=status.HTTP_204_NO_CONTENT)
