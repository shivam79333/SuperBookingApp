from django.contrib import admin
from .models import (
    Booking,
    Ticket,
    Payment,
)

myModels = [Booking, Ticket, Payment]

admin.site.register(myModels)
