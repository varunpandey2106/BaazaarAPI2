from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import Avg

from .utility import generate_upc

class Category(models.Model):


    name = models.CharField(max_length=255, help_text="Enter the category name")
    description = models.TextField(
        blank=True, null=True, help_text="Enter the category description"
    )
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def __str__(self) -> str:
        return str(self.name)

    def total_products(self):
        return self.products.count()

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ("-created_at",)


class Product(models.Model):


    upc = models.CharField(max_length=12, unique=True, blank=True)
    name = models.CharField(max_length=255, help_text="Enter the product name")
    description = models.TextField(
        blank=True, null=True, help_text="Enter the product description"
    )
    price = models.DecimalField(
        max_digits=8, decimal_places=2, help_text="Enter the product price"
    )
    quantity = models.PositiveIntegerField(
        help_text="Enter the product quantity",
        validators=[MinValueValidator(1)],
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name="products",
        help_text="Select the product category",
    )
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)

    def save(self, *args, **kwargs) -> None:
        """Override the default save method to generate a unique UPC code for product"""
        self.upc = generate_upc()
        super(Product, self).save(*args, **kwargs)

    def average_rating(self):
        """Return average rating of a product"""
        return self.reviews.aggregate(rating=Avg("rating")).get("rating")

    def __str__(self) -> str:
        return str(self.name)

    class Meta:
        ordering = ("-created_at",)


def product_image_path(instance, filename):
    """To save product image"""
    return f"product/images/{instance.product}/{filename}"


class ProductImage(models.Model):
    """
    A model representing a image of the product

    Attributes:
        product (Product): product that is associated with image
        image (Image): image of the product
        created_at (Date): date when the image is uploaded
    """

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        help_text="Select a product",
    )
    image = models.ImageField(
        upload_to=product_image_path,
        help_text="Enter the product image",
        blank=True,
    )
    created_at = models.DateField(auto_now_add=True)

    def __str__(self) -> str:
        return str(self.product)

    class Meta:
        ordering = ("-created_at",)


class Review(models.Model):
    """
    A model representing a review of the product

    Attributes:
        user (User): user of the review
        product (Product): product that is reviewed
        description (str): description of the review
        created_at (datetime): date and time when the review was created
        updated_at (datetime): date and time when the review was last updated
        rating (int): rating given by the user to the product between 1 and 5
    """

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(
        Product, on_delete=models.CASCADE, related_name="reviews"
    )
    description = models.TextField(help_text="Enter the description of the review")
    created_at = models.DateField(auto_now_add=True)
    updated_at = models.DateField(auto_now=True)
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Enter the rating of the product between 1 and 5",
    )

    def __str__(self) -> str:
        return f"{str(self.product)}_{str(self.user)}"

    class Meta:
        unique_together = ("user", "product")
        ordering = ("-created_at",)
