from django.utils import timezone
from datetime import timedelta, datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIRequestFactory, APITestCase

from devices.models import Device


class DeviceTests(APITestCase):
    def setUp(self):
        new_user1_data = {
            "username": "un",
            "first_name": "a",
            "last_name": "test",
            "password": "pw",
            "email": "test@test.com",
        }

        self.new_user1 = get_user_model().objects.create_user(
            username=new_user1_data["username"],
            first_name=new_user1_data["first_name"],
            last_name=new_user1_data["last_name"],
            email=new_user1_data["email"],
            password=new_user1_data["password"]
        )

    def test_not_allowed_device_calls(self):
        response = self.client.login(username=self.new_user1.username, password='pw')
        self.assertEqual(response, True)

        url = reverse('device-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        url = reverse('device-detail', kwargs={'sn': '1'})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        url = reverse('device-list')
        response = self.client.post(url, {'sn': '1', 'ip': '1.1.1.1'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

        url = reverse('device-detail', kwargs={'sn': '1'})
        response = self.client.put(url, {'ip': '1.1.1.1'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_health(self):
        url = reverse('device-health')
        response = self.client.post(url, {'sn': '1', 'ip': '1.1.1.1'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.login(username=self.new_user1.username, password='pw')
        self.assertEqual(response, True)

        response = self.client.post(url, {'sn': '1', 'ip': ''}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.content, b'{"ip":["This field may not be blank."]}')  # Not sure what causes this to be a required field

        response = self.client.post(url, {'sn': '1'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Device.objects.count(), 1)
        device = Device.objects.get(sn='1')
        self.assertEqual(device.name, 'חדש 1')
        self.assertEqual(device.ip, None)
        self.assertLess(abs(device.added_time - timezone.now()), timedelta(seconds=1))
        created_time = device.added_time

        response = self.client.post(url, {'sn': '1', 'ip': '1.1.1.1'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Device.objects.count(), 1)
        device = Device.objects.get(sn='1')
        self.assertEqual(device.name, 'חדש 1')
        self.assertEqual(device.ip, '1.1.1.1')
        self.assertEqual(device.added_time, created_time)
        self.assertLess(abs(device.last_reported_time - timezone.now()), timedelta(seconds=1))

        response = self.client.post(url, {'sn': '1', 'ip': '1.1.1.0'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Device.objects.count(), 1)
        self.assertEqual(Device.objects.get(sn='1').name, 'חדש 1')
        self.assertEqual(Device.objects.get(sn='1').ip, '1.1.1.0')

        response = self.client.post(url, {'sn': '2', 'ip': '2.2.2.2'}, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Device.objects.count(), 2)
        self.assertEqual(Device.objects.get(sn='2').name, 'חדש 2')
