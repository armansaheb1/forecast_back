from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('coffee-reading', views.GBuilderFile.as_view()),
]
