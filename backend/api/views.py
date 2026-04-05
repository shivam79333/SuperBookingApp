from django.shortcuts import render
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import ValidationError
from django.contrib.contenttypes.models import ContentType
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import razorpay
from django.conf import settings
from django.shortcuts import render
import datetime
from django.utils import timezone
import json


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

from . import serializers as ContentSerializer
from content import models as ContentModel
from booking import models as BookingModel
# Create your views here.


class ExperienceView(generics.RetrieveAPIView):  # returna a single object
    serializer_class = ContentSerializer.ExperienceSerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        return ContentModel.Experience.objects.filter(id=self.kwargs["id"])


class CategoryView(generics.RetrieveAPIView):
    serializer_class = ContentSerializer.CategorySerializer
    permission_classes = [AllowAny]
    lookup_field = "id"

    def get_queryset(self):
        return ContentModel.Category.objects.filter(id=self.kwargs["id"])

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


class LocationView(generics.ListAPIView):
    serializer_class = ContentSerializer.LocationSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ContentModel.Location.objects.all()


class ExperienceListView(generics.ListAPIView):
    serializer_class = ContentSerializer.ExperienceShortSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return ContentModel.Experience.objects.all()

class CreateBookingView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        serializer_class = ContentSerializer.BookingCreateSerializer(data = request.data)

        if serializer_class.is_valid():
            booking = serializer_class.save() #user_id = request.user_id, this creates the instance, as serialiser class had it already
            response_serialser = ContentSerializer.BookingDetailSerializer(booking)
            return Response(
                {
                    "message": "Booking created successfully",
                    "booking_reference": booking.booking_reference,
                    "data" : response_serialser.data
                },
                status = status.HTTP_201_CREATED
            )
        return Response(serializer_class.errors, status = status.HTTP_400_BAD_REQUEST)
    
class CreatePaymentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContentSerializer.CreatePaymentSerializer(data = request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        amount_ = int(payment.amount * 100) #amt in paise

        order_data = {
            "amount": amount_,
            "currency": "INR",
            "receipt": str(payment.booking_reference_id)
        }

        razorpay_order = client.order.create(data = order_data)
        payment.gateway_transaction_id = razorpay_order["id"] #razor pay order id
        payment.save(update_fields = ["gateway_transaction_id", "updated_at"])
        return Response(
            {
                "payment_reference": payment.payment_reference,
                "booking_reference": payment.booking_reference_id,
                "amount": amount_,
                "currency": "INR",
                "razorpay_order_id": razorpay_order["id"],
                "razorpay_key": settings.RAZORPAY_KEY_ID,
                "status": payment.status,
            },
            status=status.HTTP_201_CREATED,
        )


class CreatePaymentPageView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = ContentSerializer.CreatePaymentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payment = serializer.save()
        amount_ = int(payment.amount * 100)

        razorpay_order = client.order.create(
            data={
                "amount": amount_,
                "currency": "INR",
                "receipt": str(payment.booking_reference_id),
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
                "payment_reference": payment.payment_reference,
                "booking_reference": payment.booking_reference_id,
            },
        )

class VerifyPaymentView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payment_reference = request.data.get("payment_reference")
        razorpay_order_id = request.data.get("razorpay_order_id")
        razorpay_payment_id = request.data.get("razorpay_payment_id")
        razorpay_signature = request.data.get("razorpay_signature")

        if not all([payment_reference, razorpay_order_id, razorpay_payment_id, razorpay_signature]):
            return Response({"error": "Missing required fields"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = BookingModel.Payment.objects.get(
                payment_reference=payment_reference,
                gateway_transaction_id=razorpay_order_id,
            )
        except BookingModel.Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)

        try:
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

            booking = payment.booking_reference
            booking.status = "confirmed"
            booking.save(update_fields=["status", "updated_at"])

            return Response({"message": "Payment verified"}, status=status.HTTP_200_OK)

        except Exception:
            payment.status = "failed"
            payment.error_message = "Signature verification failed"
            payment.save(update_fields=["status", "error_message", "updated_at"])
            return Response({"error": "Verification failed"}, status=status.HTTP_400_BAD_REQUEST)





# webhook if we have keep on checking on wheter the payment successful or not, db will be updated even if frontend call misses verify

class RazorpayWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        signature = request.headers.get("X-Razorpay-Signature")
        body = request.body.decode("utf-8")

        if not signature:
            return Response({"error": "Missing signature"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            client.utility.verify_webhook_signature(
                body=body,
                signature=signature,
                secret=settings.RAZORPAY_WEBHOOK_SECRET,
            )
        except Exception:
            return Response({"error": "Invalid signature"}, status=status.HTTP_400_BAD_REQUEST)

        payload = json.loads(body)
        event = payload.get("event")

        try:
            if event == "payment.captured":
                payment_entity = payload["payload"]["payment"]["entity"]
                order_id = payment_entity.get("order_id")

                payment = BookingModel.Payment.objects.select_related("booking_reference").get(
                    gateway_transaction_id=order_id
                )

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

                payment = BookingModel.Payment.objects.get(gateway_transaction_id=order_id)
                payment.status = "failed"
                payment.error_message = error_desc
                payment.save(update_fields=["status", "error_message", "updated_at"])

            # return 200 for unhandled events too
            return Response({"message": "Webhook processed"}, status=status.HTTP_200_OK)

        except BookingModel.Payment.DoesNotExist:
            return Response({"error": "Payment not found"}, status=status.HTTP_404_NOT_FOUND)
