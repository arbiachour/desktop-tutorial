from django.urls import path
from views import hubspot_webhook

url_patterns = [
    path("webhook/", hubspot_webhook.as_view(), name='hubspot_webhook')
]