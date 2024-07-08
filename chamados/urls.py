from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChamadosViewSet

router = DefaultRouter()
router.register(r'', ChamadosViewSet)

urlpatterns = router.urls
