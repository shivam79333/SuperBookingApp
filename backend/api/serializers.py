from rest_framework import serializers
from content import models as ContentModel
from .paginations import StandardResultsSetPagination


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentModel.Experience
        fields = [
            "id",
            "name",
            "description",
            "category_id",
            "location",
            "latitude",
            "longitude",
            "image_url",
            "max_daily_capacity",
            "entry_fee_base",
            "is_open",
            "opening_time",
            "closing_time",
            "last_entry_time",
            "created_at",
            "updated_at",
            "deleted_at",
        ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentModel.Location
        fields = [
            "id",
            "name",
            "icon_url",
        ]


class ExperienceShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentModel.Experience
        fields = [
            "id",
            "name",
            "category_id",
            "location",
            "image_url",
            "entry_fee_base",
            "is_open",
        ]


class CategorySerializer(serializers.ModelSerializer):
    experiences = serializers.SerializerMethodField()

    class Meta:
        model = ContentModel.Category
        fields = ["id", "name", "description", "icon_url", "experiences"]

    def get_experiences(self, obj):
        experiences = obj.experiences.filter(deleted_at__isnull=True).order_by("id")

        # Get the request from the context
        request = self.context.get("request")

        # If there is a request, paginate the experiences
        if request:
            paginator = StandardResultsSetPagination()
            paginated_experiences = paginator.paginate_queryset(experiences, request)
            serializer = ExperienceShortSerializer(paginated_experiences, many=True)
            return paginator.get_paginated_response(serializer.data).data

        # If there is no request, return the first 10 experiences
        experiences = experiences[:10]
        return ExperienceShortSerializer(experiences, many=True).data
