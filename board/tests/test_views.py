import pytest
from django.urls import reverse
from django.test import Client
from django.contrib.auth.models import User

@pytest.mark.django_db
def test_about_page_accessible():
    client = Client()
    response = client.get(reverse('about'))  
    assert response.status_code == 200
    assert b"Sobre el sistema" in response.content or b"About" in response.content

@pytest.mark.django_db
def test_login_required_redirects_from_dashboard():
    client = Client()
    response = client.get(reverse('dashboard'))
    assert response.status_code == 302
    assert "/login" in response.url

@pytest.mark.django_db
def test_successful_login_redirects_to_dashboard():
    user = User.objects.create_user(username='admin', password='Cabc2001')
    client = Client()
    response = client.post(reverse('login'), {'username': 'admin', 'password': 'Cabc2001'})
    assert response.status_code == 302
    assert response.url == reverse('dashboard')

@pytest.mark.django_db
def test_authenticated_user_can_access_dashboard():
    user = User.objects.create_user(username='admin', password='Cabc2001')
    client = Client()
    client.login(username='admin', password='Cabc2001')
    response = client.get(reverse('dashboard'))
    assert response.status_code == 200
    assert b"Dashboard" in response.content