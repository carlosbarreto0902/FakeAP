from django.urls import path, include
from . import views
from .api_views import update_device
from rest_framework.routers import DefaultRouter
from .views import WhitelistViewSet, registrar_mac_ip
from django.conf import settings
from django.conf.urls.static import static

# Configuración API REST
router = DefaultRouter()
router.register(r'whitelist', WhitelistViewSet, basename='whitelist')

urlpatterns = [
    # ======== RUTAS WEB ========
    path('', views.root_redirect_view, name='root'),
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('about/', views.about, name='about'),
    
    # Gestión Whitelist
    path('whitelist/', views.whitelist_list, name='whitelist_list'),
    path('whitelist/add/', views.whitelist_add, name='whitelist_add'),
    path('whitelist/<int:pk>/delete/', views.whitelist_delete, name='whitelist_delete'),

    # ======== PORTAL CAUTIVO MEJORADO ========
    path('portal/', views.portal_view, name='portal'),
    path('generate_204', views.android_check),
    path('ncsi.txt', views.msft_check),
    path('redirect', views.msft_check, name='windows_redirect'),
    path('captivecheck', views.captive_check),
    path('hotspot-detect.html', views.apple_check),
    
    # Nuevos endpoints para portal
    path('apple-test/', views.apple_check, name='apple_test'),  # Endpoint específico para Apple
    path('fake-login/', views.fake_login, name='fake_login'),

    # ======== API ENDPOINTS ========
    path('api/devices/update/', update_device, name='api-update-device'),
    path('api/', include(router.urls)),
    path('api/traffic/', views.registrar_trafico, name='registrar_trafico'),
    path('api/mac_ip/', registrar_mac_ip, name='registrar_mac_ip'),
    
    # ======== MONITOREO ========
    path('mac/<str:mac_address>/', views.mac_detail, name='mac_detail'),
    path('alertas/', views.alertas_list, name='alertas_list'),
    path('capturados/', views.capturados_list, name='capturados_list'),

    # ======== REDIRECCIONES UNIVERSALES ========
    path('library/test/success.html', views.apple_check),  # Para dispositivos Apple más antiguos
    path('success.html', views.apple_check),  # Compatibilidad adicional
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)