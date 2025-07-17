from rest_framework import serializers
from .models import AllowedDevice

class AllowedDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = AllowedDevice
        fields = ['mac_address']  # Usa el nombre correcto del campo del modelo