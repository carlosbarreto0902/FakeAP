# board/utils.py

from django.core.mail import send_mail
from django.conf import settings

def enviar_alerta_email(mac, ip, hostname):
    asunto = "🚨 Alerta: Dispositivo NO autorizado detectado"
    mensaje = f"""
Se ha detectado un nuevo dispositivo NO autorizado conectado a la red:

MAC Address: {mac}
IP Address: {ip}
Hostname: {hostname}

Este dispositivo ha sido registrado por primera vez.
"""
    send_mail(
        asunto,
        mensaje,
        'FakeAP <noreply@fakeap.local>',
        ['carlos.barreto.c@uni.pe'],
        fail_silently=False,
    )