from django.db import models
from django.utils.functional import cached_property
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from order.models import Order


class Payment(models.Model):
    """
    A model to represent payment of an order

    Attributes:
        order (Order): order that this payment is associated with
        updated_at (datetime): date and time when the payment was last updated
        status (char): status of the payment, can be one of:
            - "P" (pending)
            - "C" (complete)
            - "F" (failed)
    """

    PAYMENT_PENDING = "P"
    PAYMENT_COMPLETE = "C"
    PAYMENT_FAILED = "F"

    PAYMENT_CHOICES = [
        (PAYMENT_PENDING, "Pending"),
        (PAYMENT_COMPLETE, "Complete"),
        (PAYMENT_FAILED, "Failed"),
    ]
    order = models.OneToOneField(
        Order, on_delete=models.CASCADE, related_name="payment", primary_key=True
    )
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=1, choices=PAYMENT_CHOICES, default=PAYMENT_PENDING
    )

    @cached_property
    def amount(self):
        """Return total sum payment"""
        return sum(
            [item.quantity * item.product.price for item in self.order.items.all()]
        )

    @cached_property
    def user(self):
        """Return payment user"""
        return self.order.user

    def __str__(self) -> str:
        return f"{str(self.order)}_{str(self.status)}"


class Wallet(models.Model):
    user = models.OneToOneField(
        User, null=True, on_delete=models.CASCADE)
    currency = models.CharField(max_length=50, default='NGN')
    created_at = models.DateTimeField(default=timezone.now, null=True)
    
    def __str__(self):
        return self.user.__str__()

class WalletTransaction(models.Model):

    TRANSACTION_TYPES = (
        ('deposit', 'deposit'),
        ('transfer', 'transfer'),
        ('withdraw', 'withdraw'),
    )
    wallet = models.ForeignKey(Wallet, null=True, on_delete=models.CASCADE)
    transaction_type = models.CharField(
        max_length=200, null=True,  choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=100, null=True, decimal_places=2)
    timestamp = models.DateTimeField(default=timezone.now, null=True)
    status = models.CharField(max_length=100, default="pending")
    paystack_payment_reference = models.CharField(max_length=100, default='', blank=True)

    def __str__(self):
        return self.wallet.user.__str__()
