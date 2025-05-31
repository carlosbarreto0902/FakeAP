from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from board.models import Device
from datetime import datetime

@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def update_device(request):
    data = request.data
    mac = data.get('mac')
    ip = data.get('ip')
    hostname = data.get('hostname', '')

    if not mac or not ip:
        return Response({'error': 'mac e ip son requeridos'}, status=400)

    device, created = Device.objects.update_or_create(
        mac_address=mac,
        defaults={'ip_address': ip, 'detected_at': datetime.now(), 'hostname': hostname}
    )

    return Response({'status': 'ok', 'created': created})