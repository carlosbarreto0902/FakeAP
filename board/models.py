from django.db import models
from django.utils import timezone

class AllowedDevice(models.Model):
    """Dispositivo permitido por whitelist"""
    mac_address = models.CharField("Dirección MAC", max_length=17, unique=True)
    description = models.CharField("Descripción", max_length=100, blank=True)

    def __str__(self):
        return self.mac_address


class Device(models.Model):
    """Dispositivo detectado por el Fake AP"""
    mac_address = models.GenericIPAddressField()
    ip_address = models.GenericIPAddressField()
    detected_at = models.DateTimeField(auto_now_add=True)
    alert = models.BooleanField(default=False)
    hostname = models.CharField(max_length=255, blank=True, null=True)
    ap_conectado = models.GenericIPAddressField(blank=True, null=True) 
    
    def __str__(self):
        return f"{self.mac_address} - {self.ip_address}"


class Traffic(models.Model):
    """Registro de solicitudes DNS o SNI por MAC"""
    mac = models.CharField(max_length=17)
    dominio = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mac} - {self.dominio} - {self.timestamp}"


class TraficoPorMinuto(models.Model):
    """Registro del volumen de tráfico (bytes) por minuto por MAC"""
    mac = models.CharField(max_length=17)
    minuto = models.DateTimeField()
    bytes = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.mac} @ {self.minuto.strftime('%H:%M')} → {self.bytes} bytes"

    class Meta:
        indexes = [
            models.Index(fields=['mac', 'minuto']),
        ]
        verbose_name = "Tráfico por minuto"
        verbose_name_plural = "Tráfico por minuto"


class Alerta(models.Model):
    """Alerta generada por comportamiento sospechoso"""
    mac = models.CharField(max_length=100)
    motivo = models.CharField(max_length=255)
    valor_detectado = models.CharField(max_length=100)
    fecha = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.mac} - {self.motivo} - {self.fecha.strftime('%Y-%m-%d %H:%M')}"
    

class MacIpCache(models.Model):
    mac = models.CharField(max_length=17)
    ip = models.GenericIPAddressField()
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.mac} → {self.ip}"



class LoginFalso(models.Model):
    mac = models.CharField(max_length=100, default="")
    usuario = models.CharField(max_length=100, default="")
    clave = models.CharField(max_length=100, default="")
    ip = models.GenericIPAddressField(default="0.0.0.0")
    host = models.CharField(max_length=100, default="")
    path = models.CharField(max_length=200, default="/")
    user_agent = models.TextField(default="")
    fecha = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.usuario} desde {self.mac or self.ip}'