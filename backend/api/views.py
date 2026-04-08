from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.contrib.auth.models import User
from user.models import User_Data
from booking.models import Booking
from django.conf import settings
from django.shortcuts import render
import datetime
from django.utils import timezone
import json
import razorpay
from . import serializers as ContentSerializer
from .serializers import UserDataRegisterSerializer
from .paginations import StandardResultsSetPagination
from content import models as ContentModel
from booking import models as BookingModel
from .razorpay_client import client


class CategoryView(generics.RetrieveAPIView):
    serializer_class = ContentSerializer.CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        return ContentModel.Category.objects.filter(id=self.kwargs["id"])


class ExperienceView(generics.RetrieveAPIView):
    serializer_class = ContentSerializer.ExperienceSerializer
    permission_classes = [AllowAny]
    lookup_field = "public_id"

    def get_queryset(self):
        return ContentModel.Experience.objects.filter(
            public_id=self.kwargs["public_id"]
        )


class ExperienceListView(generics.ListAPIView):
    serializer_class = ContentSerializer.ExperienceShortSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ContentModel.Experience.objects.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


class ExperienceCategoryView(generics.ListAPIView):
    serializer_class = ContentSerializer.ExperienceSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_name = self.kwargs["category"]
        return ContentModel.Experience.objects.filter(category_id__name=category_name)


class LocationListView(generics.ListAPIView):
    serializer_class = ContentSerializer.LocationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ContentModel.Location.objects.all()


class LocationView(generics.RetrieveAPIView):
    serializer_class = ContentSerializer.LocationSerializer
    permission_classes = [AllowAny]
    lookup_field = "public_id"

    def get_queryset(self):
        return ContentModel.Location.objects.filter(public_id=self.kwargs["public_id"])


class BookingView(generics.RetrieveAPIView):
    serializer_class = ContentSerializer.BookingDetailSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = "reference"

    def get_queryset(self):
        return BookingModel.Booking.objects.filter(reference=self.kwargs["reference"])


class CreateBookingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer_class = ContentSerializer.BookingCreateSerializer(
            data=request.data, context={"request": request}
        )

        if serializer_class.is_valid():
            booking = serializer_class.save()
            response_serializer = ContentSerializer.BookingDetailSerializer(booking)
            return Response(
                {
                    "message": "Booking created successfully",
                    "booking_reference": booking.reference,
                    "data": response_serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer_class.errors, status=status.HTTP_400_BAD_REQUEST)


class CreatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ContentSerializer.CreatePaymentSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)

        payment = serializer.save()
        amount_ = int(payment.amount * 100)

        order_data = {
            "amount": amount_,
            "currency": "INR",
            "receipt": str(payment.booking),
        }

        razorpay_order = client.order.create(data=order_data)
        payment.gateway_transaction_id = razorpay_order["id"]
        payment.save(update_fields=["gateway_transaction_id", "updated_at"])
        return Response(
            {
                "payment_reference": payment.reference,
                "booking_reference": payment.booking.reference,
                "amount": amount_,
                "currency": "INR",
                "razorpay_order_id": razorpay_order["id"],
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "status": payment.status,
            },
            status=status.HTTP_201_CREATED,
        )


class CreatePaymentPageView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ContentSerializer.CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        booking = serializer.validated_data["booking"]

        if hasattr(booking, "payment"):
            payment = booking.payment
            return render(
                request,
                "payments/checkout.html",
                {
                    "razorpay_key": settings.RAZORPAY_KEY_ID,
                    "razorpay_order_id": payment.gateway_transaction_id,
                    "amount": int(payment.amount * 100),
                    "currency": "INR",
                    "payment_reference": payment.reference,
                    "booking_reference": booking.reference,
                },
            )

        payment = serializer.save()
        amount_ = int(payment.amount * 100)

        razorpay_order = client.order.create(
            data={
                "amount": amount_,
                "currency": "INR",
                "receipt": str(payment.booking),
            }
        )

        payment.gateway_transaction_id = razorpay_order["id"]
        payment.save(update_fields=["gateway_transaction_id", "updated_at"])

        return render(
            request,
            "payments/checkout.html",
            {
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "razorpay_order_id": razorpay_order["id"],
                "amount": amount_,
                "currency": "INR",
                "payment_reference": payment.id,
                "booking_reference": booking.id,
            },
        )


class VerifyPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment = request.data.get("payment")
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        if not all(
            [
                payment,
                razorpay_order_id,
                razorpay_payment_id,
                razorpay_signature,
            ]
        ):
            return Response(
                {"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            payment = BookingModel.Payment.objects.get(
                reference=payment, gateway_transaction_id=razorpay_order_id
            )
        except BookingModel.Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )

        try:
            if settings.DEBUG:
                payment.status = "success"
            else:
                client.utility.verify_payment_signature(
                    {
                        "razorpay_order_id": razorpay_order_id,
                        "razorpay_payment_id": razorpay_payment_id,
                        "razorpay_signature": razorpay_signature,
                    }
                )
                payment.status = "success"
            payment.paid_at = timezone.now()
            payment.save(update_fields=["status", "paid_at", "updated_at"])

            booking = payment.booking
            booking.status = "confirmed"
            booking.save(update_fields=["status", "updated_at"])

            return Response({"message": "Payment verified"}, status=status.HTTP_200_OK)

        except razorpay.errors.SignatureVerificationError:
            payment.status = "failed"
            payment.error_message = "Signature verification failed"
            payment.save(update_fields=["status", "error_message", "updated_at"])
            return Response(
                {"error": "Verification failed"}, status=status.HTTP_400_BAD_REQUEST
            )


# webhook if we have keep on checking on wheter the payment successful or not, db will be updated even if frontend call misses verify


class RazorpayWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        signature = request.headers.get("X-Razorpay-Signature")
        body = request.body.decode("utf-8")

        if not signature:
            return Response(
                {"error": "Missing signature"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            client.utility.verify_webhook_signature(
                body=body,
                signature=signature,
                secret=settings.RAZORPAY_WEBHOOK_SECRET,
            )
        except razorpay.errors.SignatureVerificationError:
            return Response(
                {"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST
            )

        payload = json.loads(body)
        event = payload.get("event")

        try:
            if event == "payment.captured":
                payment_entity = payload["payload"]["payment"]["entity"]
                order_id = payment_entity.get("order_id")

                payment = BookingModel.Payment.objects.select_related(
                    "booking_reference"
                ).get(gateway_transaction_id=order_id)

                if payment.status != "success":
                    payment.status = "success"
                    payment.paid_at = timezone.now()
                    payment.save(update_fields=["status", "paid_at", "updated_at"])

                    booking = payment.booking_reference
                    if booking.status != "confirmed":
                        booking.status = "confirmed"
                        booking.save(update_fields=["status", "updated_at"])

            elif event == "payment.failed":
                payment_entity = payload["payload"]["payment"]["entity"]
                order_id = payment_entity.get("order_id")
                error_desc = (
                    payment_entity.get("error_description")
                    or payment_entity.get("error_reason")
                    or "Payment failed"
                )

                payment = BookingModel.Payment.objects.get(
                    gateway_transaction_id=order_id
                )
                payment.status = "failed"
                payment.error_message = error_desc
                payment.save(update_fields=["status", "error_message", "updated_at"])

            # return 200 for unhandled events too
            return Response({"message": "Webhook processed"}, status=status.HTTP_200_OK)

        except BookingModel.Payment.DoesNotExist:
            return Response(
                {"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND
            )


class HomeView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]

    def _get_paginated_category_data(
        self, category_name, display_title, request, page_query_param_name
    ):
        page_size = 6
        paginator = StandardResultsSetPagination()
        paginator.page_size = page_size
        paginator.page_query_param = (
            page_query_param_name  # Set the specific query parameter name
        )
        try:
            category = ContentModel.Category.objects.get(name=category_name)
            experiences = category.experiences.filter(deleted_at__isnull=True)

            paginated_experiences = paginator.paginate_queryset(
                experiences, request, view=self
            )
            experiences_serializer = ContentSerializer.ExperienceShortSerializer(
                paginated_experiences, many=True
            )
            return {
                "category": display_title,
                "experiences": experiences_serializer.data,
                "pagination": {
                    "count": paginator.page.paginator.count,
                    "next": paginator.get_next_link(),
                    "previous": paginator.get_previous_link(),
                    "page_size": page_size,
                    "current_page": paginator.page.number,
                },
            }
        except ContentModel.Category.DoesNotExist:
            current_page = int(request.query_params.get(page_query_param_name, 1))
            return {
                "category": display_title,
                "experiences": [],
                "pagination": {
                    "count": 0,
                    "next": None,
                    "previous": None,
                    "page_size": page_size,
                    "current_page": current_page,
                },
            }

    def get(self, request):
        # 1. Continue Booking (for authenticated users)
        if request.user.is_authenticated:
            user_data, _ = User_Data.objects.get_or_create(
                user=request.user,
                defaults={"role": "user"},
            )
            pending_bookings = Booking.objects.filter(
                user_id=user_data, status="pending", deleted_at__isnull=True
            ).order_by("-created_at")
            bookings_serializer = ContentSerializer.BookingSerializer(
                pending_bookings, many=True
            )
            continue_booking = bookings_serializer.data
        else:
            continue_booking = {}

        # 2. Get all locations
        locations = ContentModel.Location.objects.all()
        locations_serializer = ContentSerializer.LocationSerializer(
            locations, many=True
        )

        # 3. Get featured categories experiences with pagination
        featured_categories_config = [
            {"name": "Museum", "title": "Explore Museums"},
            {"name": "Amusement Park", "title": "Explore Amusement Parks"},
        ]
        featured_categories_data = [
            self._get_paginated_category_data(
                config["name"],
                config["title"],
                request,
                f"{config['name'].lower().replace(' ', '_')}_page",
            )
            for config in featured_categories_config
        ]

        # 4. Get all categories with links
        all_categories = ContentModel.Category.objects.all().order_by("name")
        categories_data = []
        for category in all_categories:
            categories_data.append(
                {
                    "id": category.id,
                    "name": category.name,
                    "icon_url": category.icon_url,
                }
            )

        response_data = {
            "continue_booking": continue_booking,
            "explore_locations": {
                "label": "Explore Locations",
                "data": locations_serializer.data,
                "link": reverse("location_list", request=request),
            },
            "featured_categories": featured_categories_data,
            "all_categories": categories_data,
        }

        return Response(response_data)


class SignupView(generics.CreateAPIView):
    serializer_class = UserDataRegisterSerializer
    permission_classes = [AllowAny]
    queryset = User_Data.objects.all()
