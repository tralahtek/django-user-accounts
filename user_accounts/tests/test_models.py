from django.test import TestCase
from rest_framework.test import APITestCase
from django.test import Client
from django.contrib.auth import get_user_model
import unittest

User = get_user_model()
# Create your tests here.


class UserAPITestCase(APITestCase):
    def setUp(self):
        self.usr = User(phonenumber="+254741997729", username="TralahTek", is_secretary=True, is_superuser=True)
        self.usr.set_password("password")
        self.usr.save()
        self.usr1 = User(phonenumber="+252724032913", username="Mohan56", is_producer=True)
        self.usr1.set_password("password")
        self.usr1.save()

    def test_user_secretary(self):
        self.assertEqual(self.usr.is_secretary, True)

    def test_user_producer(self):
        self.assertEqual(self.usr1.is_producer, True)

    def test_user_superuser(self):
        self.assertEqual(self.usr.is_superuser, True)
