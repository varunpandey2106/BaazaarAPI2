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

##APP DEV CLASS GIT COMMANDS DEMO

from django.db import transaction

class DepositSerializer(serializers.Serializer):
    amount = serializers.IntegerField(validators=[is_amount])
    email = serializers.EmailField()

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            return value
        raise serializers.ValidationError({"detail": "Email not found"})

    def save(self):
        user = self.context["request"].user

        # Ensure atomicity of the operation
        with transaction.atomic():
            # Get or create the Wallet object for the user
            wallet, created = Wallet.objects.get_or_create(user=user)

            # Update balance and create transaction
            data = self.validated_data
            url = "https://api.paystack.co/transaction/initialize"
            headers = {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
            r = requests.post(url, headers=headers, data=data)
            response = r.json()
            WalletTransaction.objects.create(
                wallet=wallet,
                transaction_type="deposit",
                amount=data["amount"],
                paystack_payment_reference=response["data"]["reference"],
                status="pending",
            )

        return response
