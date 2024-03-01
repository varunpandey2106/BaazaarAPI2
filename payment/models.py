from django.db import models
from django.utils.functional import cached_property

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


# from django.db import models
# from user.models import User
# from django.dispatch import receiver
# from django.db.models.signals import post_save

# class UserPayment(models.Model):
# 	user = models.ForeignKey(User, on_delete=models.CASCADE)
# 	payment_bool = models.BooleanField(default=False)
# 	stripe_checkout_id = models.CharField(max_length=500)


# @receiver(post_save, sender=User)
# def create_user_payment(sender, instance, created, **kwargs):
# 	if created:
# 		UserPayment.objects.create(app_user=instance)
