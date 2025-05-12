from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    cooling = models.BooleanField()
    price = models.FloatField()

class Team(models.Model):
    name = models.CharField(max_length=255)
    pick_up_location = models.CharField(max_length=255)

class CustomerContact(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)

class Address(models.Model):
    contact = models.ForeignKey(CustomerContact, on_delete=models.CASCADE)
    street = models.CharField(max_length=255)
    zip_code = models.CharField(max_length=10)
    city = models.CharField(max_length=100)
    gmaps_link = models.CharField(max_length=255)

class Installation(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product)
    address = models.ForeignKey(Address, on_delete=models.CASCADE)
    installation_date = models.DateField()


class WebhookLog(models.Model):
    class Status(models.Choices):
        INPROGRESS = "INPROGRESS" 
        RECIEVED = "RECIEVED" 
        PROCESSED = "PROCESSED"
        FAILED = "FAILED" 
    event_type = models.CharField(max_length=100)
    payload = models.JSONField()
    status = models.CharField(max_length=50, choices=Status.choices, default=Status.RECIEVED)
    received_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    error = models.TextField(blank=True, null=True)