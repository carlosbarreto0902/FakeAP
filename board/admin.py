from django.contrib import admin
from .models import Device, AllowedDevice


admin.site.register(Device)

class AllowedDeviceAdmin(admin.ModelAdmin):
    list_display = ('mac_address', 'description')
    search_fields = ('mac_address',)