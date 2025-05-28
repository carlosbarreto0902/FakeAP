from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Device, AllowedDevice
from .forms import AllowedDeviceForm

@login_required
def dashboard(request):
    devices = Device.objects.order_by('-detected_at')
    return render(request, 'board/dashboard.html', {'devices': devices})

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