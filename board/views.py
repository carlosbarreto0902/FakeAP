from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Device, AllowedDevice
from .forms import AllowedDeviceForm
from datetime import date
from django.utils.timezone import localtime

# Django REST Framework
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from .serializers import AllowedDeviceSerializer
from .utils import enviar_alerta_email


# Vistas web

@login_required
def dashboard(request):
    devices = Device.objects.order_by('-detected_at')

    # Obtener la fecha actual (en zona local)
    hoy = date.today()
    alerta = False
    whitelist = set(AllowedDevice.objects.values_list('mac_address', flat=True))

    for d in devices:
        # Convertir a zona local si es necesario
        detected_date = localtime(d.detected_at).date()
        if d.mac_address not in whitelist and detected_date == hoy:
            alerta = True
            break

    # Marcar dispositivos permitidos
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


# API REST: Whitelist solo lectura
class WhitelistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AllowedDevice.objects.all()
    serializer_class = AllowedDeviceSerializer
    permission_classes = [AllowAny]  # Usa IsAuthenticated si deseas requerir login en producción


# API para registrar dispositivos detectados
@api_view(['POST'])
@permission_classes([AllowAny])
def update_device(request):
    mac = request.data.get('mac_address')
    ip = request.data.get('ip_address')
    hostname = request.data.get('hostname', '')

    if not mac or not ip:
        return Response({'error': 'Faltan datos'}, status=400)

    ya_existe = Device.objects.filter(mac_address=mac).exists()
    esta_en_whitelist = AllowedDevice.objects.filter(mac_address=mac).exists()

    # Registrar nuevo dispositivo
    device = Device.objects.create(
        mac_address=mac,
        ip_address=ip,
        hostname=hostname,
        alert=not esta_en_whitelist
    )

    # Debug para consola
    print(f"Debug: MAC={mac}, YaExiste={ya_existe}, EnWhitelist={esta_en_whitelist}")

    # Enviar alerta si es nuevo y no está permitido
    if not ya_existe and not esta_en_whitelist:
        print(f"✅ ALERTA: Enviando correo para {mac}")
        enviar_alerta_email(mac, ip, hostname)

    return Response({'status': 'ok'})