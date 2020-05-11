"""
Author: TralahM
Helper Module to send Push notifications to bmb android apk devices
to be used to ensure users are notified of events in realtime if and when SMS
medium fails or is delayed.

"""
from fcm_django.models import FCMDevice
from django.utils.translation import gettext_lazy as _


def fcm_push_msg(uids=[], message="", title="BIZ Notification"):
    title = _(title)
    devices = FCMDevice.objects.filter(user__id__in=uids)
    devices.send_message(title=str(title), body=str(message))


def new_app_version():
    title = "New App Update Available"
    title = _(title)
    message = "Get the Latest BIZ App Version"
    message = _(message)
    devices = FCMDevice.objects.all()
    devices.send_message(title=str(title), body=str(message))
