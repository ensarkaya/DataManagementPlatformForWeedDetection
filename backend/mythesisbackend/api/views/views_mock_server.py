from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import time
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from datetime import datetime

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def mock_ml_server(request):
    start_time = datetime.now()
    print(f"Task started at {start_time}")

    time.sleep(5)  # Simulated delay

    end_time = datetime.now()
    print(f"Task finished at {end_time}, duration: {end_time - start_time}")
    response_data = {"message": "Analysis complete", "status": "success"}
    return Response(response_data, status=status.HTTP_200_OK)
