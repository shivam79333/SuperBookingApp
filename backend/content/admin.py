from django.contrib import admin
from .models import (
    State,
    City,
    Category,
    Experience,
    PricingRule,
    OperatingHours,
    Provider,
    TicketType,
    Collection,
    CollectionExperience,
)

myModels = [
    State,
    City,
    Category,
    Experience,
    PricingRule,
    OperatingHours,
    Provider,
    TicketType,
    Collection,
    CollectionExperience,
]

admin.site.register(myModels)
