from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('about/', views.about, name='about'),
    path('whitelist/', views.whitelist_list, name='whitelist_list'),
    path('whitelist/add/', views.whitelist_add, name='whitelist_add'),
    path('whitelist/<int:pk>/delete/', views.whitelist_delete, name='whitelist_delete'),
]