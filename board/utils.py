from django.core.mail import send_mail
from django.conf import settings
from django.utils.timezone import now
from .models import Alerta

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

    Alerta.objects.create(
        mac=mac,
        motivo="Nuevo dispositivo detectado",
        valor_detectado=f"{ip} / {hostname}",
        fecha=now()
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

    Alerta.objects.create(
        mac=mac,
        motivo=motivo,
        valor_detectado=valor,
        fecha=now()
    )

def enviar_alerta_login_fake(usuario, clave, ip, host, path):
    asunto = f"🛑 Intento de login capturado - Honeypot"
    mensaje = f"""
Se ha capturado un intento de autenticación en el portal falso del honeypot:

Usuario: {usuario}
Clave: {clave}
IP: {ip}
Host: {host}
Path: {path}

Este intento podría estar relacionado a una intrusión o prueba no autorizada.
"""
    remitente = getattr(settings, 'EMAIL_HOST_USER', 'FakeAP <noreply@fakeap.local>')

    send_mail(
        asunto,
        mensaje,
        remitente,
        ['carlos.barreto.c@uni.pe'],
        fail_silently=False,
    )

    # Registrar alerta en la base de datos
    Alerta.objects.create(
        mac=ip,
        motivo="Intento de login falso capturado",
        valor_detectado=f"{usuario} / {clave}",
        fecha=now()
    )