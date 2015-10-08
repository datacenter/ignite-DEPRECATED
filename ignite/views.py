from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response

from serializer import IgniteSerializer
from ignite import process_ignite


class Ignite(APIView):

    def post(self, request, format=None):
        serializer = IgniteSerializer(data=request.data)

        if serializer.is_valid():
            # process the ignite request
            result = process_ignite(request.data)

            return Response(result, status=status.HTTP_201_CREATED)
            
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
