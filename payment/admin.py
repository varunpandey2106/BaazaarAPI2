from django.contrib import admin
from .models import Payment, UserPayment

# Register your models here.

admin.site.register(Payment)
admin.site.register(UserPayment)