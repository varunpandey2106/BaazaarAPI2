from rest_framework import serializers

from .models import Payment


class ReadPaymentSerializer(serializers.ModelSerializer):
    """Serializer class of Payment model for reading payment [GET]"""

    class Meta:
        model = Payment
        fields = ["order_id", "amount", "status", "created_at", "updated_at"]

    order_id = serializers.IntegerField(source="order.id")
    created_at = serializers.StringRelatedField(source="order.created_at")


class WritePaymentSerializer(serializers.ModelSerializer):
    """Serializer class of Review model for writing payment [PATCH]"""

    class Meta:
        model = Payment
        fields = ["status"]

# import datetime

# from rest_framework import serializers


# def check_expiry_month(value):
#     if not 1 <= int(value) <= 12:
#         raise serializers.ValidationError("Invalid expiry month.")


# def check_expiry_year(value):
#     today = datetime.datetime.now()
#     if not int(value) >= today.year:
#         raise serializers.ValidationError("Invalid expiry year.")


# def check_cvc(value):
#     if not 3 <= len(value) <= 4:
#         raise serializers.ValidationError("Invalid cvc number.")


# def check_payment_method(value):
#     payment_method = value.lower()
#     if payment_method not in ["card"]:
#         raise serializers.ValidationError("Invalid payment_method.")

# class CardInformationSerializer(serializers.Serializer):
#     card_number = serializers.CharField(max_length=150, required=True)
#     expiry_month = serializers.CharField(
#         max_length=150,
#         required=True,
#         validators=[check_expiry_month],
#     )
#     expiry_year = serializers.CharField(
#         max_length=150,
#         required=True,
#         validators=[check_expiry_year],
#     )
#     cvc = serializers.CharField(
#         max_length=150,
#         required=True,
#         validators=[check_cvc],
#     )