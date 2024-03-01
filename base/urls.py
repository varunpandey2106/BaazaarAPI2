"""base URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

from django.urls import re_path
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi


schema_view = get_schema_view(
   openapi.Info(
      title="Baazaar API 2.0",
      default_version='v1',
      description="This is version 2 of BaazaarAPI,an ecom API, with optimized code and overall better documentation",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="varun.pandey2106@gmail.com"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
   permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path("user/", include("user.urls")),
    path('accounts/', include('allauth.urls')),
    path("store/", include("product.urls")),
    path("order/", include("order.urls")),
    path("cart/", include("cart.urls")),
    path("payment/", include("payment.urls")),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path("auth/", include("djoser.urls"))



]
