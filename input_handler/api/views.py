from rest_framework.views import APIView
from rest_framework.response import Response
from ..models import UploadedImage
from .serializers import UploadedImageSerializer

class ItemsView(APIView):
    def get(self, request):
        items = UploadedImage.objects.all()
        serializer = UploadedImageSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UploadedImageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)