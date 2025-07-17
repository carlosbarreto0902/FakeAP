import pytest
from django.test import Client
from django.urls import reverse
from board.models import WhitelistDevice

@pytest.mark.django_db
def test_mac_is_in_whitelist():
    # Creamos un dispositivo permitido
    WhitelistDevice.objects.create(mac_address="AA:BB:CC:DD:EE:FF")

    # Simulamos que una función de validación (que tú implementas) detecta la MAC
    mac = "AA:BB:CC:DD:EE:FF"
    assert WhitelistDevice.objects.filter(mac_address=mac).exists()

@pytest.mark.django_db
def test_mac_is_not_in_whitelist():
    mac = "11:22:33:44:55:66"
    assert not WhitelistDevice.objects.filter(mac_address=mac).exists()


