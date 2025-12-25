import logging
from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import get_user_model
from .user_serializers import (
    UserSerializer,
    UserRegistrationSerializer,
    UserProfileUpdateSerializer,
    PasswordChangeSerializer
)

logger = logging.getLogger('main')
User = get_user_model()


class UserRegistrationView(generics.CreateAPIView):
    """
    API endpoint for user registration
    """
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        logger.info(f"New user registered: {user.username}")
        
        return Response(
            {
                'message': 'ثبت‌نام با موفقیت انجام شد.',
                'user': UserSerializer(user).data
            },
            status=status.HTTP_201_CREATED
        )


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    API endpoint for viewing and updating user profile
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UserProfileUpdateSerializer
        return UserSerializer


class UserDetailView(generics.RetrieveAPIView):
    """
    API endpoint for viewing other users' public profiles
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'username'

    def get_serializer_context(self):
        context = super().get_serializer_context()
        # Only show limited info for other users
        context['public_profile'] = True
        return context


class PasswordChangeView(APIView):
    """
    API endpoint for changing user password
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PasswordChangeSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = request.user
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            logger.info(f"Password changed for user: {user.username}")
            
            return Response(
                {'message': 'رمز عبور با موفقیت تغییر یافت.'},
                status=status.HTTP_200_OK
            )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user_view(request):
    """
    API endpoint to get current authenticated user info
    """
    serializer = UserSerializer(request.user)
    return Response(serializer.data)

