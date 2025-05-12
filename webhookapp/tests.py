import json
from django.test import TestCase, Client
from django.urls import reverse
from django.utils.crypto import constant_time_compare
import hmac
import hashlib

class HubSpotWebhookTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.token = "toekn-hubspot"
        self.url = reverse("hubspot_webhook")

    def generate_signature(self, body):
        return hmac.new(
            key=self.token.encode(),
            msg=body,
            digestmod=hashlib.sha256
        ).hexdigest()

    def test_invalid_method(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 405)

    def test_missing_signature(self):
        response = self.client.post(self.url, data={})
        self.assertEqual(response.status_code, 403)

    def test_invalid_signature(self):
        body = json.dumps({"some": "data"}).encode()
        response = self.client.post(self.url, data=body, content_type='application/json', HTTP_X_HUBSPOT_SIGNATURE='invalid')
        self.assertEqual(response.status_code, 403)

    def test_valid_signature_invalid_payload(self):
        payload = json.dumps({"objectId": "test", "propertyName": "dealstage", "propertyValue": "165866736"})
        signature = self.generate_signature(payload.encode())
        response = self.client.post(
            self.url,
            data=payload,
            content_type='application/json',
            HTTP_X_HUBSPOT_SIGNATURE=signature
        )
        self.assertEqual(response.status_code, 400)  # Expect failure due to mock ID

# Note: For full integration test, mock `HSWebhook` with a valid HubSpot sandbox or use `unittest.mock