import logging

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from backends.async_send_mail import send_email_async
from backends.permission import IsAdminOrReadOnly
from order.models import Order

from .models import Payment
from .permission import IsAuthorizedAndPaymentNotComplete
from .serializer import ReadPaymentSerializer, WritePaymentSerializer
import requests
from rest_framework.decorators import action


logger = logging.getLogger(__name__)


# STRIPE

class PaymentViewset(ModelViewSet):
    """A viewset for Payment model"""

    http_method_names = ["get", "patch", "delete"]
    permission_classes = [IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        """Overriding to return user specific order"""
        if self.request.user.is_staff:
            return Payment.objects.select_related("order").all()
        return Payment.objects.select_related("order").filter(
            order__user=self.request.user
        )

    def get_serializer_class(self):
        """Overriding to return serializer class based on HTTP method"""
        if self.request.method == "PATCH":
            return WritePaymentSerializer
        return ReadPaymentSerializer


stripe.api_key = settings.STRIPE_SECRET_KEY


from rest_framework import status

class CreateStripeCheckoutSession(APIView):
    """
    Create and return checkout session ID for order payment of type 'Stripe'
    """

    permission_classes = [IsAuthenticated, IsAuthorizedAndPaymentNotComplete]

    def post(self, request, *args, **kwargs):
        order = get_object_or_404(Order, id=self.kwargs.get("order_id"))
        order_items = []
        for item in order.items.all():
            product = item.product
            quantity = item.quantity
            data = {
                "price_data": {
                    "currency": "usd",
                    "unit_amount_decimal": product.price,
                    "product_data": {
                        "name": product.name,
                        "description": product.description,
                    },
                },
                "quantity": quantity,
            }
            order_items.append(data)

        logger.info("Creating Stripe Session")
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=order_items,
                metadata={"order_id": order.id},
                mode="payment",
                success_url=settings.PAYMENT_SUCCESS_URL,
                cancel_url=settings.PAYMENT_CANCEL_URL,
            )
            return Response(
                {"sessionId": checkout_session["id"], "url": checkout_session["url"]},
                status=status.HTTP_201_CREATED,
            )
        except Exception as e:
            logger.error(f"Stripe Error while creating checkout {e}")
            return Response({"error": "Error creating checkout session"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    """
    Stripe webhook view to handle checkout session completed event.
    """

    permission_classes = [IsAuthenticated, IsAuthorizedAndPaymentNotComplete]

    def post(self, request, format=None):
        payload = request.body
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        sig_header = request.META["HTTP_STRIPE_SIGNATURE"]
        event = None

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, endpoint_secret)
        except ValueError as e:
            logger.error(f"Error in stripe webhook while constructing event {e}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Error in stripe webhook while constructing event {e}")
            return HttpResponse(status=400)

        if event["type"] == "checkout.session.completed":
            print("Payment successful")
            session = event["data"]["object"]

            customer_email = session["customer_details"]["email"]
            order_id = session["metadata"]["order_id"]

            payment = Payment.objects.get(pk=order_id)
            payment.status = "C"
            payment.save()

            send_email_async.delay(
                to_email=customer_email,
                subject="Thank you for purchasing",
                message=f"Your order {order_id} have been placed",
                from_email="shopapi89@gmail.com",
            )

        return HttpResponse(status=200)




def initiate_payment(amount, email, order_id):
    url = "https://api.flutterwave.com/v3/payments"
    headers = {
        "Authorization": f"Bearer {settings.FLW_SEC_KEY}"
        
    }
    
    data = {
        "amount": str(amount), 
        "currency": "USD",
        "redirect_url": "http:/127.0.0.1:8000/api/orders/confirm_payment/?o_id=" + order_id,
        "meta": {
            "consumer_id": 23,
            "consumer_mac": "92a3-912ba-1192a"
        },
        "customer": {
            "email": email,
            "phonenumber": "080****4528",
            "name": "Yemi Desola"
        },
        "customizations": {
            "title": "Pied Piper Payments",
            "logo": "http://www.piedpiper.com/app/themes/joystick-v27/images/logo.png"
        }
    }
    

    try:
        response = requests.post(url, headers=headers, json=data)
        response_data = response.json()
        return Response(response_data)
    
    except requests.exceptions.RequestException as err:
        print("the payment didn't go through")
        return Response({"error": str(err)}, status=500)


##PAYSTACK


import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view
from django.contrib.auth import authenticate
from django.conf import settings

from .models import Wallet, WalletTransaction
from .serializer import UserSerializer, WalletSerializer, DepositSerializer


class Login(APIView):
    permission_classes = ()

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(username=username, password=password)
        if user:
            return Response({"token": user.auth_token.key, "username": username})
        else:
            return Response(
                {"error": "Wrong Credentials"}, status=status.HTTP_400_BAD_REQUEST
            )


class Register(APIView):
    authentication_classes = ()
    permission_classes = ()

    def post(self, request):

        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class WalletInfo(APIView):
    def get(self, request):
        wallet = Wallet.objects.get(user=request.user)
        data = WalletSerializer(wallet).data
        return Response(data)


class DepositFunds(APIView):
    def post(self, request):
        serializer = DepositSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        resp = serializer.save()
        return Response(resp)


class VerifyDeposit(APIView):
    def get(self, request, reference):
        transaction = WalletTransaction.objects.get(
            paystack_payment_reference=reference, wallet__user=request.user
        )
        reference = transaction.paystack_payment_reference
        url = "https://api.paystack.co/transaction/verify/{}".format(reference)
        headers = {"authorization": f"Bearer {settings.PAYSTACK_SECRET_KEY}"}
        
        r = requests.get(url, headers=headers)
        resp = r.json()
        if resp["data"]["status"] == "success":
            status = resp["data"]["status"]
            amount = resp["data"]["amount"]
            WalletTransaction.objects.filter(
                paystack_payment_reference=reference
            ).update(status=status, amount=amount)
            return Response(resp)
        return Response(resp)
