# HubSpot Webhook Integration (Django)

This Django app connects to HubSpot using webhooks to automatically sync deal and installation data into your database when a deal changes stage.

## 🚀 Features

- Verifies HubSpot webhook signatures
- Parses deal, contact, and line item info via HubSpot API
- Calculates pricing based on installation type and subsidy
- Saves:
  - Customer contact
  - Installation address
  - Installation team
  - Product details and pricing

---

## ⚙️ Setup Instructions

1. **Clone the repo & install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure your environment**
   - Ensure you have a valid **HubSpot Private App Token**
   - Update it in `views.py` and `hubspot_service.py`

3. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Run the server**
   ```bash
   python manage.py runserver
   ```

---

## 🧪 Running Tests

Run the basic unit tests:
```bash
python manage.py test tests/
```

---

## 📌 Webhook Endpoint

- **POST** `/hubspot-webhook/`
- Header: `X-HubSpot-Signature`
- Body must include:
  ```json
  {
    "objectId": "DEAL_ID",
    "propertyName": "dealstage",
    "propertyValue": "165866736"
  }
  ```

---

## 🔐 Security

- Webhook requests are verified using HMAC SHA-256 and your HubSpot token.
- Ensure you use HTTPS in production.

---

## 🛠️ To Do

- Add mock tests for the full `HSWebhook` pipeline
- Log errors to a monitoring tool (e.g., Sentry)
- Support retries on API failure

---

## 👤 Author

Developed by Mohamed Arbi Achour 