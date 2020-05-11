from django.urls import path
from django.conf.urls import include
from user_accounts import views as uacc_views
from rest_framework.routers import SimpleRouter

router = SimpleRouter()
router.register(r"users", uacc_views.UserViewSet, basename="User")
router.register(r"allusers", uacc_views.AllUserViewSet, basename="AllUser")
router.register(r"accounts", uacc_views.AccountViewSet, basename="Account")
router.register(r"transactions", uacc_views.TransactionViewSet,
                basename="Transaction")

urlpatterns = [
    path("", router.urls),
]
