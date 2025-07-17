from django.contrib import admin
from django.urls import path, include
from board.views import logout_confirm_view
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ======== ADMINISTRACIÓN ========
    path('admin/', admin.site.urls),
    
    # ======== AUTENTICACIÓN ========
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', logout_confirm_view, name='logout'),
    
    # ======== RUTAS PRINCIPALES ========
    path('', include('board.urls')),  # Incluye todas las rutas de board/urls.py
]