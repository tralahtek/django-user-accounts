# from django.utils.translation import gettext_lazy as _
import africastalking


#username = "betmebackdrc"
#api_key = "9582bc66e076c3af93b2b09f20ba4fb0d0b91d4623bee91871fbb36e482ceb8d"


#africastalking.initialize(username, api_key)
b_username = "fep"

b_api_key = "abeec2507fc5c375c17a3b1aecf2465a27d409e52a7ed3cca8518beceae29053"
api_key = "c775027d4d1f8c95213629bdb6d6877f164583c6a7e60c2974a775bf469bfc19"

africastalking.initialize(b_username, api_key)

SMS = africastalking.SMS


def send_message(recipients=[], message=""):
    try:
        SMS.send(message, recipients, "FEP-GROUP")
    except Exception as e:
        print(e)
        pass


# FCM (Firebase Cloud Messaging Confs)
notification = {
    "to": "registration_id",
    "notification": {
        "title": "Confirmed Deposit into your BMB wallet",
        "body": "Confirmed Deposit of 234000 into your BMB wallet new wallet balance is 234000",
        "icon": "bmb_icon.png",
    }
}
data_message = {
    "to": "registration_id",
    "data": {
        "inviter": "TralahM",
        "invited": "more",
        "stake": "100",
        "game": "23499",
        "is_accepted": False,
        "is_pending": True,
    },
}
