from django.core.mail import send_mail
from django.conf import settings

def enviar_alerta_email(mac, ip, hostname):
    asunto = "🚨 Alerta: Dispositivo detectado en la red"
    mensaje = f"""
Se ha detectado un nuevo dispositivo conectado a la red:

MAC Address: {mac}
IP Address: {ip}
Hostname: {hostname}

Este dispositivo ha sido registrado por primera vez.
"""
    remitente = getattr(settings, 'EMAIL_HOST_USER', 'FakeAP <noreply@fakeap.local>')

    send_mail(
        asunto,
        mensaje,
        remitente,
        ['carlos.barreto.c@uni.pe'],
        fail_silently=False,
    )

def enviar_alerta_trafico_sospechoso(mac, motivo, valor):
    asunto = f"⚠️ Alerta de tráfico sospechoso - {mac}"
    mensaje = f"""
Se ha detectado un comportamiento anómalo en el dispositivo con la siguiente dirección MAC:

MAC Address: {mac}
Motivo: {motivo}
Valor detectado: {valor}

Se recomienda investigar esta actividad para descartar un posible ataque.
"""
    remitente = getattr(settings, 'EMAIL_HOST_USER', 'FakeAP <noreply@fakeap.local>')

    send_mail(
        asunto,
        mensaje,
        remitente,
        ['carlos.barreto.c@uni.pe'],
        fail_silently=False,
    )