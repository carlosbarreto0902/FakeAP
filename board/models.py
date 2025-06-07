from django.db import models

class AllowedDevice(models.Model):
    mac_address = models.CharField("Dirección MAC", max_length=17, unique=True)
    description = models.CharField("Descripción", max_length=100, blank=True)

    def __str__(self):
        return self.mac_address

class Device(models.Model):
    mac_address = models.CharField(max_length=17, unique=True)  # <-- aquí el cambio
    ip_address = models.GenericIPAddressField()
    detected_at = models.DateTimeField(auto_now_add=True)
    alert = models.BooleanField(default=False)
    hostname = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"{self.mac_address} - {self.ip_address}"
    
class WhitelistDevice(models.Model):
    mac_address = models.CharField(max_length=17, unique=True)

    def __str__(self):
        return self.mac_address    