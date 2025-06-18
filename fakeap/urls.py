"""
URL configuration for fakeap project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from board.views import logout_confirm_view, portal_fake_view
from django.contrib.auth import views as auth_views
from django.http import HttpResponse


urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('accounts/logout/', logout_confirm_view, name='logout'),
    path('', include('board.urls')),

    # ⚠️ Detección automática de portal (modo aeropuerto)
    path('generate_204', lambda request: HttpResponse("", status=200)),
    path('hotspot-detect.html', lambda request: HttpResponse("<HTML><BODY>Success</BODY></HTML>", content_type='text/html', status=200)),
    path('connecttest.txt', lambda request: HttpResponse("Microsoft Connect Test", content_type='text/plain', status=200)),

    # 🧲 Fallback para cualquier otra URL HTTP
    re_path(r'^.*$', portal_fake_view),
]