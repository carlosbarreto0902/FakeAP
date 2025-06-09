from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Device, AllowedDevice, Traffic, TraficoPorMinuto
from .forms import AllowedDeviceForm
from datetime import date
from django.utils.timezone import now, timedelta
from django.db.models import Count
from collections import Counter
from datetime import timedelta as dtimedelta
# Django REST Framework
from rest_framework import viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response

from .serializers import AllowedDeviceSerializer
from .utils import enviar_alerta_email

import pytz
from datetime import datetime

# -------------------------
# Vistas Web
# -------------------------

@login_required
def dashboard(request):
    devices = Device.objects.order_by('-detected_at')

    hoy = date.today()
    alerta = False
    whitelist = set(AllowedDevice.objects.values_list('mac_address', flat=True))

    for d in devices:
        detected_date = d.detected_at.date()
        if d.mac_address not in whitelist and detected_date == hoy:
            alerta = True
            break

    for d in devices:
        d.is_allowed = d.mac_address in whitelist

    return render(request, 'board/dashboard.html', {
        'devices': devices,
        'alerta': alerta
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


# -------------------------
# API REST: Whitelist solo lectura
# -------------------------

class WhitelistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AllowedDevice.objects.all()
    serializer_class = AllowedDeviceSerializer
    permission_classes = [AllowAny]


# -------------------------
# API: Registro de tráfico autenticado
# -------------------------

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
        return Response({'status': 'ok'})

    elif 'bytes' in request.data and 'minuto' in request.data:
        try:
            minuto_str = request.data['minuto']
            # Convertir string a datetime naive
            minuto_naive = datetime.strptime(minuto_str, '%Y-%m-%d %H:%M')

            # Asignar zona horaria local (Lima)
            local_tz = pytz.timezone('America/Lima')
            minuto_local_aware = local_tz.localize(minuto_naive)

            # Convertir a UTC
            minuto_utc = minuto_local_aware.astimezone(pytz.UTC)

            bytes_usados = int(request.data['bytes'])

            obj, created = TraficoPorMinuto.objects.update_or_create(
                mac=mac,
                minuto=minuto_utc,
                defaults={'bytes': bytes_usados}
            )
            return Response({'status': 'ok'})

        except Exception as e:
            return Response({'error': str(e)}, status=400)

    return Response({'error': 'Datos incompletos'}, status=400)


# -------------------------
# Vista para detalle de tráfico por MAC
# -------------------------

@login_required
def mac_detail(request, mac_address):
    # Últimos 100 registros de tráfico de dominios para esta MAC
    registros = Traffic.objects.filter(mac=mac_address).order_by('-timestamp')[:100]

    hora_actual = now()
    hace_1hora = hora_actual - timedelta(hours=1)

    # Tráfico DNS en la última hora para agrupar por minuto
    ultimos = Traffic.objects.filter(mac=mac_address, timestamp__gte=hace_1hora)

    # Conteo de solicitudes DNS por minuto (hora local Lima)
    conteo = {}
    for r in ultimos:
        minuto_local = r.timestamp.astimezone(pytz.timezone('America/Lima')).strftime('%H:%M')
        conteo[minuto_local] = conteo.get(minuto_local, 0) + 1

    datos_grafico = [
        {'minuto': k, 'total': conteo[k]}
        for k in sorted(conteo)
    ]

    # Tráfico bytes por minuto en la última hora
    registros_bytes = TraficoPorMinuto.objects.filter(
        mac=mac_address,
        minuto__gte=hace_1hora
    ).only('minuto', 'bytes').order_by('minuto')

    local_tz = pytz.timezone('America/Lima')

    # Ajuste de tiempo restando 5 horas en la hora mostrada
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