from rest_framework import mixins
from rest_framework import parsers
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from user_accounts.models import User, Account, Transaction
from user_accounts.serializers import UserSerializer, AccountSerializer, TransactionSerializer, AllUserSerializer
from rest_framework.schemas import AutoSchema
from rest_framework import filters
import coreapi

from django.contrib.auth import logout


# Create your views here.
class CreateListRetrieveViewset(mixins.ListModelMixin,
                                mixins.CreateModelMixin,
                                mixins.RetrieveModelMixin,
                                viewsets.GenericViewSet):
    pass


class UserViewSetSchema(AutoSchema):
    def get_manual_fields(self, path, method):
        extra_fields = []
        if method.lower() in ['post', 'put', 'patch']:
            extra_fields = [
                coreapi.Field('phonenumber'),
                coreapi.Field('username'),
            ]
            manual_fields = super().get_manual_fields(path, method)
            return manual_fields + extra_fields


class AllUserViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [permissions.IsAuthenticated, ]
    serializer_class = AllUserSerializer
    lookup_field = "username"
    filter_backends = [filters.SearchFilter, ]
    search_fields = ['username', 'phonenumber']

    def get_queryset(self):
        return User.objects.all()


class CLRUpdateViewset(mixins.UpdateModelMixin, CreateListRetrieveViewset):
    pass


class UserViewSet(CLRUpdateViewset):
    schema = UserViewSetSchema()
    permission_classes = [permissions.AllowAny]
    parser_classes = (parsers.MultiPartParser, parsers.JSONParser, parsers.FormParser,)
    # queryset = User.objects.all()
    serializer_class = UserSerializer
    http_method_names = ['get', 'post', 'head', 'put', 'patch']
    lookup_field = "username"

    def get_queryset(self):
        # user = self.request.user
        if self.request.user.is_authenticated:
            if self.request.user.is_producer or self.request.user.is_secretary or self.request.user.is_staff:
                return User.objects.all()
            else:
                return self.request.user
        else:
            return User.objects.none()

    @action(detail=False, methods=['GET'])
    def current(self, request):
        return Response(self.serializer_class(self.request.user).data)

    @action(detail=True, methods=['POST'])
    def set_password(self, request, phonenumber=None):
        """ Set new user Pasword  """
        user = self.get_object()
        # phonenumber = request.data['phonenumber']
        # username = request.data['username']
        password = request.data['password']
        user.set_password(password)
        user.save()
        return Response({'status': 'password set'})

    @action(detail=False, methods=['POST'])
    def reset_password(self, request, *args, **kwargs):
        phonenumber = request.data['phonenumber']
        u = User.objects.filter(phonenumber__icontains=phonenumber).first()
        if u is not None:
            u.gen_otp()
            u.set_password(u.otp)
            u._send_otp()
            return Response({'status': 'Success!'})
        else:
            return Response({'status': 'User not Found!'})


class AccountViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = AccountSerializer

    def get_queryset(self):
        user = self.request.user
        return Account.objects.filter(owner=user)


class TransactionViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TransactionSerializer
    # queryset = Transaction.objects.all()

    def get_queryset(self):
        wallet = self.request.user.wallet
        return Transaction.objects.filter(account=wallet).exclude(title__icontains="ACCOUNT OPENING")
