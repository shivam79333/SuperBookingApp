from django.contrib import admin
from .models import (
    Category,
    Experience,
    PricingRule,
    OperatingHours,
)

myModels = [Category, Experience, PricingRule, OperatingHours]

admin.site.register(myModels)
