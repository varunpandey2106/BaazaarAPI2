from django.contrib import admin
from .models import Payment, Wallet, WalletTransaction

# Register your models here.

admin.site.register(Payment)
admin.site.register(Wallet)
admin.site.register(WalletTransaction)
