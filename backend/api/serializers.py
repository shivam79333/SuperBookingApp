from rest_framework import serializers
from content import models as ContentModel
from booking import models as BookingModel
from user.models import User_Data
from django.contrib.auth.models import User as AuthUser
from .paginations import StandardResultsSetPagination
import uuid



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




class BookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingModel.Booking
        fields = [
            "booking_reference",
            "user_id",
            "experience_id",
            "booking_date",
            "slot_time",
            "total_tickets",
            "total_amount",
            "status",
            "cancelled_at",
            "cancellation_reason",
            "refund_amount",
            "refund_status",
            "special_requests",
            "created_at",
            "updated_at",
            "deleted_at",
        ]
        read_only_fields = ["booking_reference", "created_at", "updated_at", "cancelled_at"]


class BookingCreateSerializer(serializers.ModelSerializer):
    """For POST requests - minimal required fields"""
    user_id = serializers.PrimaryKeyRelatedField(queryset=AuthUser.objects.all())

    class Meta:
        model = BookingModel.Booking
        fields = [
            "user_id",
            "experience_id",
            "booking_date",
            "slot_time",
            "total_tickets",
            # "total_amount",
            "special_requests",
        ]

    def validate_user_id(self, auth_user):
        try:
            return auth_user.user_data
        except User_Data.DoesNotExist:
            raise serializers.ValidationError("No profile found for this user.")

    def create(self, validated_data):
        experience = validated_data["experience_id"]
        tickets = validated_data["total_tickets"]
        validated_data["total_amount"] = experience.entry_fee_base * tickets
        return BookingModel.Booking.objects.create(**validated_data)


class BookingDetailSerializer(serializers.ModelSerializer):
    """For GET requests - includes related object details"""
    user = serializers.StringRelatedField(source="user_id", read_only=True)
    experience = ExperienceShortSerializer(source="experience_id", read_only=True)

    class Meta:
        model = BookingModel.Booking
        fields = [
            "booking_reference",
            "user",
            "experience",
            "booking_date",
            "slot_time",
            "total_tickets",
            "total_amount",
            "status",
            "refund_status",
            "special_requests",
            "created_at",
        ]


class CreatePaymentSerializer(serializers.ModelSerializer):
    booking_reference = serializers.PrimaryKeyRelatedField(
        queryset=BookingModel.Booking.objects.all()
    ) #get all the booking_refences

    class Meta:
        model = BookingModel.Payment
        fields = [
            "booking_reference",
            "payment_method",
            "payment_gateway",
        ]

    def validate_booking_reference(self, booking):
        if booking.status == "cancelled":
            raise serializers.ValidationError("Cannot create payment for cancelled booking.")
        if hasattr(booking, "payment"):
            raise serializers.ValidationError("Payment already exists for this booking.")
        return booking

    def create(self, validated_data):
        booking = validated_data["booking_reference"]
        return BookingModel.Payment.objects.create(
            payment_reference=f"PAY-{uuid.uuid4().hex[:14].upper()}",
            booking_reference=booking,
            user_id=booking.user_id,
            amount=booking.total_amount,
            status="pending",
            **{k: v for k, v in validated_data.items() if k != "booking_reference"},
        )