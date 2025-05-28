from django import forms
from .models import AllowedDevice

class AllowedDeviceForm(forms.ModelForm):
    class Meta:
        model = AllowedDevice
        fields = ['mac_address', 'description']