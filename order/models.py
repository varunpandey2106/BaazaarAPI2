from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.db import models
from django.utils.functional import cached_property

from product.models import Product
from user.models import Address


class Order(models.Model):


    DELIVERY_PENDING = "P"
    DELIVERY_COMPLETE = "C"
    DELIVERY_FAILED = "F"

    DELIVERY_CHOICES = [
        (DELIVERY_PENDING, "Pending"),
        (DELIVERY_COMPLETE, "Complete"),
        (DELIVERY_FAILED, "Failed"),
    ]

    user = models.ForeignKey(User, on_delete=models.PROTECT)
    billing_address = models.ForeignKey(
        Address, on_delete=models.PROTECT, related_name="billed_orders"
    )
    shipping_address = models.ForeignKey(
        Address, on_delete=models.PROTECT, related_name="shipped_orders"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    delivery = models.CharField(
        max_length=1, choices=DELIVERY_CHOICES, default=DELIVERY_PENDING
    )

    @cached_property
    def total_price(self):
        """Return total order price"""
        return sum([item.quantity * item.product.price for item in self.items.all()])

    def __str__(self) -> str:
        return f"{str(self.user)}_{str(self.created_at)}"

    class Meta:
        ordering = ("-created_at",)


class OrderItem(models.Model):


    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="orders",
        help_text="Select an product to order",
    )
    ordered_price = models.DecimalField(max_digits=8, decimal_places=2)
    quantity = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1)],
        help_text="Enter the product quantity",
    )

    @cached_property
    def total_price(self):
        """Return order item total price"""
        return self.ordered_price * self.quantity

    def __str__(self) -> str:
        return f"{str(self.order)}_{str(self.product)}"

    class Meta:
        ordering = ("-quantity",)
