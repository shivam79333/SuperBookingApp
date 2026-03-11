from rest_framework import serializers
from content import models as ContentModel


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
