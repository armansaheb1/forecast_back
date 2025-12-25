from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .tarot_views import TarotCardsView, TarotReadingView
from .dream_interpretation_view import DreamInterpretationView
from .tarot_image_views import get_tarot_card_image
from .user_views import (
    UserRegistrationView,
    UserProfileView,
    UserDetailView,
    PasswordChangeView,
    current_user_view
)
from .profile_views import FortuneProfileViewSet

# Create router for ViewSets
router = DefaultRouter()
router.register(r'profiles', FortuneProfileViewSet, basename='profile')

urlpatterns = [
    # Coffee Reading
    path('coffee-reading/', views.GBuilderFile.as_view(), name='coffee-reading'),
    
    # Horoscope Reading
    path('horoscope', views.HoroscopeView.as_view(), name='horoscope'),
    
    # I Ching Reading
    path('iching', views.IChingView.as_view(), name='iching'),
    
    # Dream Interpretation
    path('dream-interpretation', DreamInterpretationView.as_view(), name='dream-interpretation'),
    
    # Tarot Reading
    path('tarot/cards/', TarotCardsView.as_view(), name='tarot-cards'),
    path('tarot/reading/', TarotReadingView.as_view(), name='tarot-reading'),
    path('tarot/cards/<int:card_id>/image/', get_tarot_card_image, name='tarot-card-image'),
    
    # User Management
    path('auth/register/', UserRegistrationView.as_view(), name='user-register'),
    path('auth/profile/', UserProfileView.as_view(), name='user-profile'),
    path('auth/me/', current_user_view, name='current-user'),
    path('auth/change-password/', PasswordChangeView.as_view(), name='change-password'),
    path('users/<str:username>/', UserDetailView.as_view(), name='user-detail'),
    
    # Profile Management (ViewSet routes)
    path('', include(router.urls)),
]
