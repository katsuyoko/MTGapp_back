import google.oauth2.credentials
import requests

from django.conf import settings
from django.forms.models import model_to_dict
from django.db import models
#from django.contrib.auth.models import User


# Create your models here.
class Credentials(models.Model):
    token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255, blank=True)
    token_uri = models.CharField(max_length=255)
    client_id = models.CharField(max_length=255)
    client_secret = models.CharField(max_length=255)
    scopes = models.CharField(max_length=255)
    expiry = models.DateTimeField()
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.user

    def to_dict(self):
        return model_to_dict(self, exclude=('id', 'user'))

    @property
    def auth(self):
        """[summary]
        Return:
            (google.oauth2.credentials.Credentials)
        """
        if not hasattr(self, '_auth'):
            self._auth = google.oauth2.credentials.Credentials(**self.to_dict())
        return self._auth

    def revoke(self):
        """Google側の認証情報を削除し、このモデルインスタンスも削除する"""
        requests.post(
            'https://accounts.google.com/o/oauth2/revoke',
            params={'token': self.auth.token},
            headers={'content-type': 'application/x-www-form-urlencoded'}
        )
        self.delete()
