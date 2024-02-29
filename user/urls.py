from rest_framework_nested.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from . import views

router = DefaultRouter()

router.register("profile", views.ProfileViewset, "profile")
router.register("address", views.AddressViewset, "address")

urlpatterns = router.urls

