import json
import pytest

from django.contrib.auth.models import User
from django.test import Client

from rest_framework import status


class TestLogin:
    user_details = {
        'username': '019191911',
        'email': 'tim@timsdomain.com',
        'first_name': 'Tim',
        'last_name': 'Morris',
        'password': 'thisismypassword'
    }

    @pytest.mark.django_db
    def test_login_success(self):
        user = User.objects.create_user(**self.user_details)

        resp = Client().post('/auth/login/', json.dumps({
            'username': user.username,
            'password': 'thisismypassword'
        }), content_type='application/json')

        assert resp.status_code == status.HTTP_200_OK

    @pytest.mark.django_db
    def test_login_failure(self):
        user = User.objects.create_user(**self.user_details)

        resp = Client().post('/auth/login/', json.dumps({
            'username': user.username,
            'password': 'thisisNOTmypassword'
        }), content_type='application/json')

        assert resp.status_code == status.HTTP_400_BAD_REQUEST
