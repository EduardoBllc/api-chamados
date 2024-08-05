from rest_framework.routers import DefaultRouter
from django.urls import path
from .views import VariaveisSettings

urlpatterns = [
    path('var_settings/', VariaveisSettings.as_view(), name='var_settings'),
]
