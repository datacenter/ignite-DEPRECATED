from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from serializer import POAPSerializer
from poap import process_poap


class POAP(APIView):

    def post(self, request, format=None):
        serializer = POAPSerializer(data=request.data)

        if serializer.is_valid():
            # process the poap request
            result = process_poap(request.data)

            return Response(result, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
