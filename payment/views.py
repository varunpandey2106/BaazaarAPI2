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

logger = logging.getLogger(__name__)


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



# from django.shortcuts import render, redirect
# from django.conf import settings
# from django.contrib.auth.decorators import login_required
# from django.views.decorators.csrf import csrf_exempt
# from django.http import HttpResponse
# from .models import UserPayment
# import stripe
# import time


# # @login_required(login_url='login')
# def product_page(request):
# 	stripe.api_key = settings.STRIPE_SECRET_KEY
# 	if request.method == 'POST':
# 		checkout_session = stripe.checkout.Session.create(
# 			payment_method_types = ['card'],
# 			line_items = [
# 				{
# 					'price': settings.PRODUCT_PRICE,
# 					'quantity': 1,
# 				},
# 			],
# 			mode = 'payment',
# 			customer_creation = 'always',
# 			success_url = settings.REDIRECT_DOMAIN + '/payment_successful?session_id={CHECKOUT_SESSION_ID}',
# 			cancel_url = settings.REDIRECT_DOMAIN + '/payment_cancelled',
# 		)
# 		return redirect(checkout_session.url, code=303)
# 	return render(request, 'payment/product_page.html')


# ## use Stripe dummy card: 4242 4242 4242 4242
# def payment_successful(request):
# 	stripe.api_key = settings.STRIPE_SECRET_KEY
# 	checkout_session_id = request.GET.get('session_id', None)
# 	session = stripe.checkout.Session.retrieve(checkout_session_id)
# 	customer = stripe.Customer.retrieve(session.customer)
# 	user_id = request.user.user_id
# 	user_payment = UserPayment.objects.get(app_user=user_id)
# 	user_payment.stripe_checkout_id = checkout_session_id
# 	user_payment.save()
# 	return render(request, 'payment/payment_successful.html', {'customer': customer})


# def payment_cancelled(request):
# 	stripe.api_key = settings.STRIPE_SECRET_KEY
# 	return render(request, 'payment/payment_cancelled.html')


# @csrf_exempt
# def stripe_webhook(request):
# 	stripe.api_key = settings.STRIPE_SECRET_KEY
# 	time.sleep(10)
# 	payload = request.body
# 	signature_header = request.META['HTTP_STRIPE_SIGNATURE']
# 	event = None
# 	try:
# 		event = stripe.Webhook.construct_event(
# 			payload, signature_header, settings.STRIPE_WEBHOOK_SECRET
# 		)
# 	except ValueError as e:
# 		return HttpResponse(status=400)
# 	except stripe.error.SignatureVerificationError as e:
# 		return HttpResponse(status=400)
# 	if event['type'] == 'checkout.session.completed':
# 		session = event['data']['object']
# 		session_id = session.get('id', None)
# 		time.sleep(15)
# 		user_payment = UserPayment.objects.get(stripe_checkout_id=session_id)
# 		user_payment.payment_bool = True
# 		user_payment.save()
# 	return HttpResponse(status=200)



# from rest_framework.views import APIView
# from rest_framework.response import Response
# from .serializer import CardInformationSerializer
# import stripe


# class PaymentAPI(APIView):
#     serializer_class = CardInformationSerializer

#     def post(self, request):
#         serializer = self.serializer_class(data=request.data)
#         response = {}
#         if serializer.is_valid():
#             data_dict = serializer.data
          
#             stripe.api_key = 'your-key-goes-here'
#             response = self.stripe_card_payment(data_dict=data_dict)

#         else:
#             response = {'errors': serializer.errors, 'status':
#                 status.HTTP_400_BAD_REQUEST
#                 }
                
#         return Response(response)


#     def stripe_card_payment(self, data_dict):
#         try:
#             card_details = {
#                 "type": "card",
#                 "card": {
#                     "number": data_dict['card_number'],
#                     "exp_month": data_dict['expiry_month'],
#                     "exp_year": data_dict['expiry_year'],
#                     "cvc": data_dict['cvc'],
#                 }
#             }
#             #  you can also get the amount from databse by creating a model
#             payment_intent = stripe.PaymentIntent.create(
#                 amount=10000, 
#                 currency='inr',
#             )
#             payment_intent_modified = stripe.PaymentIntent.modify(
#                 payment_intent['id'],
#                 payment_method=card_details['id'],
#             )
#             try:
#                 payment_confirm = stripe.PaymentIntent.confirm(
#                     payment_intent['id']
#                 )
#                 payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
#             except:
#                 payment_intent_modified = stripe.PaymentIntent.retrieve(payment_intent['id'])
#                 payment_confirm = {
#                     "stripe_payment_error": "Failed",
#                     "code": payment_intent_modified['last_payment_error']['code'],
#                     "message": payment_intent_modified['last_payment_error']['message'],
#                     'status': "Failed"
#                 }
#             if payment_intent_modified and payment_intent_modified['status'] == 'succeeded':
#                 response = {
#                     'message': "Card Payment Success",
#                     'status': status.HTTP_200_OK,
#                     "card_details": card_details,
#                     "payment_intent": payment_intent_modified,
#                     "payment_confirm": payment_confirm
#                 }
#             else:
#                 response = {
#                     'message': "Card Payment Failed",
#                     'status': status.HTTP_400_BAD_REQUEST,
#                     "card_details": card_details,
#                     "payment_intent": payment_intent_modified,
#                     "payment_confirm": payment_confirm
#                 }
#         except:
#             response = {
#                 'error': "Your card number is incorrect",
#                 'status': status.HTTP_400_BAD_REQUEST,
#                 "payment_intent": {"id": "Null"},
#                 "payment_confirm": {'status': "Failed"}
#             }
#         return response
