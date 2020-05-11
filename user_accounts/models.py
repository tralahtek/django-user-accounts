from countries_plus.models import Country
from decimal import Decimal as D
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import FieldError
from django.db import models
from django.db.models import Sum
from django.utils.crypto import get_random_string
from phonenumber_field.modelfields import PhoneNumberField
from phonenumbers import carrier, geocoder
from phonenumbers import timezone as ptimezone
from user_accounts import sms
import string


# Create your models here.


class UserManager(BaseUserManager):
    """ A model manager with no username field """

    use_in_migrations = True

    def get_queryset(self):
        return super().get_queryset().select_related("wallet")

    def _create_user(self, phonenumber, password, **extra_fields):
        """ Create and Save a User with given phonenumber and password """
        if not phonenumber:
            raise ValueError("Phonenumber must be set")
        user = self.model(phonenumber=phonenumber, **extra_fields)
        middle_name = extra_fields.get("middle_name", "")
        address = extra_fields.get("address", "")
        first_name = extra_fields.get("first_name", "")
        last_name = extra_fields.get("last_name", "")
        email = extra_fields.get("email", "")
        user.middle_name = middle_name
        user.address = address
        user.email = email
        user.first_name = first_name
        user.last_name = last_name
        user.otp = get_random_string(4, string.digits)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, phonenumber, password=None, **extra_fields):
        """Create and save a regular User with the given phonenumber and password."""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        extra_fields.setdefault("is_active", True)
        # extra_fields.setdefault('confirmed_at', False)
        return self._create_user(phonenumber, password, **extra_fields)

    def create_superuser(self, phonenumber, password, **extra_fields):
        """Create and save a SuperUser with the given phonenumber and password.""" ""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(phonenumber, password, **extra_fields)


class User(AbstractUser):
    """
    Representing a User
    Some relations are to Account, Appointment providing relations as
    account,appointments
    Defined methods
    + _create_account
    + _create_appointment
    """

    phonenumber = PhoneNumberField(
        max_length=20, verbose_name="phonenumber", unique=True
    )
    username = models.CharField(
        max_length=20, verbose_name="username", unique=True)
    first_name = models.CharField(max_length=20, null=True)
    middle_name = models.CharField(max_length=20, null=True)
    address = models.CharField(max_length=120, null=True)
    last_name = models.CharField(max_length=20, null=True)
    otp = models.CharField(max_length=20, null=True)
    uuid = models.CharField(max_length=100, null=True, default=None)
    avatar = models.ImageField(upload_to="avatars/%Y/%m/%d", null=True)
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["phonenumber"]
    objects = UserManager()

    def _create_account(self):
        return Account.objects.create(owner=self, is_active=True)

    def gen_otp(self):
        self.otp = get_random_string(4, string.digits)
        self.save()

    def _send_otp(self):
        message = f"""
        <#>\n
        TralahTek: Your  Verifiction Code is : {self.otp} \n
        """
        sms.send_message(
            recipients=[str(self.phonenumber)], message=message.strip())

    def __str__(self):
        return str(self.username)

    @property
    def carrier_name(self):
        return carrier.name_for_number(self.phonenumber, "en")

    @property
    def timezone(self):
        return ptimezone.time_zones_for_number(self.phonenumber)[0]

    @property
    def ph_region_code(self):
        return geocoder.region_code_for_number(self.phonenumber).strip()

    @property
    def country(self):
        return Country.objects.get(iso__iexact=self.ph_region_code)


class AccountManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("owner")


class Account(models.Model):
    """
    Representing a User Account
    Relations are to User, Transaction providing relations as
    owner,transactions
    methods defined are:
    + validate_amount
    + _create_transaction
    + calculate_balance
    + credit_account
    + debit_account
    """

    owner = models.OneToOneField(
        "user_accounts.User", on_delete=models.CASCADE, related_name="wallet"
    )
    balance = models.DecimalField(
        verbose_name="Account Balance",
        max_digits=12,
        decimal_places=2,
        default=D("0.0"),
    )
    is_active = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)
    is_deleted = models.BooleanField(default=False)
    objects = AccountManager()

    def _create_transaction(self, trans_type, amount, title=""):
        amount = self.validate_amount(amount)
        if trans_type == "DEBIT":
            if amount > self.balance:
                raise FieldError(
                    f"Insufficient Funds to  Complete Transaction of Amount {amount}"
                )
            if amount < 0:
                raise FieldError(f"Invalid Amount {amount} !")
            # amount = amount*-1
        return Transaction.objects.create(
            account=self, trans_type=trans_type, amount=amount, title=title
        )

    @staticmethod
    def validate_amount(amount):
        if not isinstance(amount, (int, D, str)):
            raise FieldError("Value needs to be a string,integer or Decimal!")
        return D(amount)

    def debit_account(self, amount, title="Withdraw Funds"):
        amount = self.validate_amount(amount)
        self._create_transaction(
            trans_type="DEBIT", amount=amount, title=title)
        self.balance = self.balance - amount
        self.save()

    def credit_account(self, amount, title="Deposit Funds"):
        amount = self.validate_amount(amount)
        self._create_transaction(
            trans_type="CREDIT", amount=amount, title=title)
        self.balance = self.balance + amount
        self.save()

    def update_current_balance(self):
        if (
            self.transactions.filter(trans_type="DEBIT", is_pending=False).aggregate(
                total=Sum("amount")
            )["total"]
            is not None
        ):
            self.balance = (
                self.transactions.filter(
                    trans_type="CREDIT", is_pending=False
                ).aggregate(total=Sum("amount"))["total"]
                - self.transactions.filter(
                    trans_type="DEBIT", is_pending=False
                ).aggregate(total=Sum("amount"))["total"]
            )
            self.save()
        self.save()

    def __str__(self):
        return str(self.owner.phonenumber) + " \t " + str(self.balance)


class TransactionManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().select_related("account")


class Transaction(models.Model):
    """Model for Transactions on an Account."""

    title = models.CharField(max_length=255, blank=True)
    trans_type = models.CharField(
        max_length=255, choices=(("DEBIT", "DEBIT"), ("CREDIT", "CREDIT"))
    )
    account = models.ForeignKey(
        "user_accounts.Account", on_delete=models.CASCADE, related_name="transactions"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_pending = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    objects = TransactionManager()

    def __str__(self):
        return (
            self.trans_type
            + " , "
            + str(self.created_at.date())
            + " , "
            + str(self.created_at.time())
            + " , "
            + str(self.amount)
            + " , "
            + self.title
        )
