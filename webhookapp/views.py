from datetime import timezone
import hmac
import hashlib
from models import Installation, CustomerContact, Address, Product, Team, WebhookLog
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
import json
from hubspot_service import HSWebhook 
import logging

logger = logging.getLogger("hubspot")
handler = logging.FileHandler("hubspot_webhook.log")
formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

HUBSPOT_TOKEN = "hubspot-token"
PIPELINE_TYPE = {
    'default': 'AO',
    '350385367': 'PT',
    '350385364': 'DWE',
    '39929315': 'HC',
}

PIPELINE_STAGE = [
             '91937997', 
             '548472308', 
             '548342492', 
             '165866736', 
             '548472309', 
             '548342493', 
]

@csrf_exempt
def hubspot_webhook(request):
    if request.method != "POST":
        return JsonResponse({'error':'Invalid method'}, status=405)
    else:
        signature = request.headers.get("X-HubSpot-Signature")
        if not signature:
            return JsonResponse({"error": "Missing Signature"}, status=403)

        computed_signature = hmac.new(
            key=HUBSPOT_TOKEN.encode(),
            msg=request.body,
            digestmod=hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(signature, computed_signature):
            return HttpResponseForbidden("Invalid signature")
        
        try:
            #Process deal
            hook = json.loads(request.body)
            logger.info(f"Received webhook payload: {request.body.decode()}")
            log_entry = WebhookLog.objects.create(
                event_type=hook.get("propertyName", "unknown"),
                payload=hook,
                status= WebhookLog.Status.RECIEVED
            )
            hook_property_name = hook.propertyName
            deal_stage = hook.propertyValue
            if deal_stage not in PIPELINE_STAGE or hook_property_name is not 'dealstage':
                return JsonResponse({'status':'failed'}, status=400)
            
            deal_id = hook.objectId 
            hs_values = HSWebhook(deal_id)   
            
            # Create or update customer contact
            contact, _ = CustomerContact.objects.update_or_create(
                email=hs_values.customer_contact_info.get("email"),
                defaults={
                    "full_name": f"{hs_values.customer_contact_info.get('first_name', '')} {hs_values.customer_contact_info.get('last_name', '')}",
                    "phone": hs_values.customer_contact_info.get("phone"),
                }
            )

            # Address
            address, _ = InstallationAddress.objects.update_or_create(
                contact=contact,
                defaults={
                    "street": hs_values.contact_address.get("street"),
                    "zip_code": hs_values.contact_address.get("zip_code"),
                    "city": hs_values.contact_address.get("city"),
                    "gmaps_link": hs_values.contact_address.get("g_maps_link"),
                }
            )

            # Team
            team, _ = InstallationTeam.objects.update_or_create(
                name=hs_values.installation_information.get("team"),
                defaults={
                    "pick_up_location": hs_values.installation_information.get("team_pick_up_location"),
                }
            )
            installation = Installation.objects.create(
                team=team,
                address=address,
                first_installation_date=hs_values.installation_information.get("first_installation_day"),
                second_installation_date=...,
                work_preparation_by=hs_values.installation_information.get("work_preparation_by"),
                work_preparation_note=hs_values.installation_information.get("work_preparation_note"),
            )
            for product_data in hs_values.products:
                product, _ = InstallationProduct.objects.get_or_create(
                    name=product_data["name"],
                    type=product_data["type"],
                    cooling=product_data["cooling"],
                    price=product_data["price"]
                )
                installation.products.add(product)
            

            log_entry.status = WebhookLog.Status.PROCESSED
            log_entry.processed_at = timezone.now()
            log_entry.save()

            return JsonResponse({'status': "success"}, status=200)
        except Exception as e:
            log_entry.status = WebhookLog.Status.FAILED
            log_entry.error = str(e)
            log_entry.save()
            return JsonResponse({"error": f"error occured while processing deal {e}"},status=400)


