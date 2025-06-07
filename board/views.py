from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Device, AllowedDevice
from .forms import AllowedDeviceForm
from datetime import date
from django.utils.timezone import localtime, now

# Django REST Framework
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .serializers import AllowedDeviceSerializer
from .utils import enviar_alerta_email


# Vistas web

@login_required
def dashboard(request):
    devices = Device.objects.order_by('-detected_at')

    hoy = date.today()
    alerta = False
    whitelist = set(AllowedDevice.objects.values_list('mac_address', flat=True))

    for d in devices:
        detected_date = localtime(d.detected_at).date()
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


# API REST: Whitelist solo lectura
class WhitelistViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AllowedDevice.objects.all()
    serializer_class = AllowedDeviceSerializer
    permission_classes = [AllowAny]