"""
user_accounts.signals.handlers
defining some signals to trigger some custom actions that occur when our
models are created, saved and updated
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from user_accounts.models import Transaction, User
from user_accounts import sms
from user_accounts.notifications import fcm_push_msg
from decimal import Decimal as D
import decimal

decimal.getcontext().prec = 6


def sanitize_phone(pn):
    """
    To avoid africastalking sms phonenumber is invalid when we want to send
    messages
    and for multi-national phonenummber support
    """
    return str(pn)


@receiver(post_save, sender=User)
def create_user_account(sender, instance, created, **kwargs):
    """
    Create an account for a user once a user is created
    """
    if created:
        instance._create_account()
        instance.wallet._create_transaction(
            trans_type="CREDIT", amount="0.0", title="ACCOUNT OPENING"
        )
        instance.wallet._create_transaction(
            trans_type="DEBIT", amount="0.0", title="ACCOUNT OPENING"
        )


@receiver(post_save, sender=Transaction)
def update_account_balance_after_transaction(sender, instance, **kwargs):
    """
    When a transaction is created we update the balance of the account
    and notify the user that the appropriate transaction has taken place
    """
    instance.account.update_current_balance()
    if (
        instance.trans_type == "CREDIT"
        and "WAGER" not in instance.title.upper()
        and "ACCOUNT OPENING" not in instance.title.upper()
    ):
        msg = f"""
        Confirmed Deposit of {instance.account.owner.country.currency_code} {instance.amount} to Account: {instance.account.owner.phonenumber} on {instance.created_at} \n
        New Wallet Balance is : {instance.account.owner.country.currency_code}  {instance.account.balance}
        """
        rec = [sanitize_phone(instance.account.owner.phonenumber)]
        sms.send_message(recipients=rec, message=msg.strip())
        fcm_push_msg(
            uids=[instance.account.owner.id],
            message=msg.strip(),
            title="Business Payment",
        )
    if (
        instance.trans_type == "DEBIT"
        and instance.amount > 0
        and "PEER" not in instance.title.upper()
        and "ACCOUNT OPENING" not in instance.title.upper()
    ):
        msg = f"""
        Confirmed on {instance.created_at}  you have received {instance.account.owner.country.currency_code}: {instance.amount} from your BMB Wallet
        Your new wallet balance is {instance.account.owner.country.currency_code}: {instance.account.balance}
        """
        rec = [sanitize_phone(instance.account.owner.phonenumber)]
        sms.send_message(recipients=rec, message=msg.strip())
        fcm_push_msg(
            uids=[instance.account.owner.id],
            message=msg.strip(),
            title="Business Payout",
        )


def create_transaction(sender, instance, **kwargs):
    current_user = User.objects.get(
        phonenumber__in=[instance.phonenumber, "0" + instance.phonenumber[4:]]
    )
    if current_user:
        current_user.wallet._create_transaction(
            trans_type="CREDIT", amount=instance.amount, title=instance.transaction_id
        )
