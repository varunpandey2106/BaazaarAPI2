from django.urls import include, path
from rest_framework_nested.routers import DefaultRouter

from .views import Login, Register, WalletInfo, DepositFunds, VerifyDeposit

# router = DefaultRouter()
# router.register(prefix="payment", viewset=views.PaymentViewset, basename="payment")

# custom_urls = [
#     path(
#         "stripe/payment/<int:order_id>/",
#         views.CreateStripeCheckoutSession.as_view(),
#         name="checkout_session",
#     ),
#     path("webhooks/stripe/", views.StripeWebhookView.as_view(), name="stripe-webhook"),
# ]

# urlpatterns = [
#     path("", include(router.urls)),
#     path("", include(custom_urls)),
# ]


# from django.urls import path
# from .views import PaymentAPI

# urlpatterns = [
#     path('make_payment/', PaymentAPI.as_view(), name='make_payment')
# ]


# from django.urls import path
# from . import views

# urlpatterns = [
# 	path('product_page', views.product_page, name='product_page'),
# 	path('payment_successful', views.payment_successful, name='payment_successful'),
# 	path('payment_cancelled', views.payment_cancelled, name='payment_cancelled'),
# 	path('stripe_webhook', views.stripe_webhook, name='stripe_webhook'),
# ]

urlpatterns = [
    path('register/', Register.as_view()),
    path('login/', Login.as_view()),
    path('wallet_info/', WalletInfo.as_view()),
    path('deposit/', DepositFunds.as_view()),
    path('deposit/verify/<str:reference>/', VerifyDeposit.as_view()),
]
