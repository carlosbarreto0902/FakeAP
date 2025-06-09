from django.urls import path, include
from . import views
from .api_views import update_device

# Django REST Framework
from rest_framework.routers import DefaultRouter
from .views import WhitelistViewSet

# Registrar vista API REST para whitelist
router = DefaultRouter()
router.register(r'whitelist', WhitelistViewSet, basename='whitelist')

urlpatterns = [
    # Rutas web
    path('', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('whitelist/', views.whitelist_list, name='whitelist_list'),
    path('whitelist/add/', views.whitelist_add, name='whitelist_add'),
    path('whitelist/<int:pk>/delete/', views.whitelist_delete, name='whitelist_delete'),

    # Rutas API
    path('api/devices/update/', update_device, name='api-update-device'),
    path('api/', include(router.urls)),  # <- Incluye las rutas de la API REST (como /api/whitelist/)
    path('api/traffic/', views.registrar_trafico, name='registrar_trafico'),
    path('mac/<str:mac_address>/', views.mac_detail, name='mac_detail'),
]