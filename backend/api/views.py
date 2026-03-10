from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType

from . import serializers as ContentSerializer
from content import models as ContentModel
# Create your views here.


class ExperienceView(generics.RetrieveAPIView):
    serializer_class = ContentSerializer.ExperienceSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        return ContentModel.Experience.objects.filter(id=self.kwargs["id"])
