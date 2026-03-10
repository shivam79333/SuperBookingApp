from django.db import models
from django.contrib.auth.hashers import make_password, check_password


class Booking(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
        ('completed', 'Completed'),
    ]

    REFUND_STATUS_CHOICES = [
        ('none', 'None'),
        ('requested', 'Requested'),
        ('processed', 'Processed'),
        ('failed', 'Failed'),
    ]

    booking_reference   = models.CharField(max_length=50, null=False, unique=True)
    user                = models.ForeignKey('User', on_delete=models.CASCADE, related_name='bookings')
    monument            = models.ForeignKey('Monument', on_delete=models.CASCADE, related_name='bookings')
    booking_date        = models.DateField(null=False)
    slot_time           = models.TimeField(blank=True, null=True)
    total_tickets       = models.IntegerField(null=False)
    total_amount        = models.DecimalField(max_digits=10, decimal_places=2, null=False)
    payment             = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    status              = models.CharField(max_length=20, choices=STATUS_CHOICES, null=False, default='pending')
    cancelled_at        = models.DateTimeField(blank=True, null=True)
    cancellation_reason = models.TextField(blank=True, null=True)
    refund_amount       = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    refund_status       = models.CharField(max_length=20, choices=REFUND_STATUS_CHOICES, blank=True, null=True)
    special_requests    = models.TextField(blank=True, null=True)
    created_at          = models.DateTimeField(auto_now_add=True)
    updated_at          = models.DateTimeField(auto_now=True)
    deleted_at          = models.DateTimeField(blank=True, null=True)

    def cancel(self, reason=None):
        """Cancel the booking with an optional reason."""
        from django.utils import timezone
        self.status = 'cancelled'
        self.cancelled_at = timezone.now()
        self.cancellation_reason = reason
        self.save()

    def is_cancelled(self):
        return self.status == 'cancelled'

    def __str__(self):
        return f"Booking {self.booking_reference} - {self.status}"

    class Meta:
        db_table = 'bookings'
        ordering = ['-booking_date']
