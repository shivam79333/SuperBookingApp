from django.contrib import admin
from .models import User_Data

myModels = [User_Data]

admin.site.register(myModels)
