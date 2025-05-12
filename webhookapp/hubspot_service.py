import datetime
import hubspot
from hubspot.crm.deals import ApiException as DealApiException
from hubspot.crm.contacts import ApiException as ContactApiException
from hubspot.crm.line_items import ApiException as LineItemApiException
from hubspot.crm.associations.v4 import BatchInputPublicFetchAssociationsBatchRequest
from hubspot.crm.associations.v4 import ApiException as AssociationApiException


POMP_T_SUBSIDY = float(950)
SUBSIDY_BEFORE_2024 = float(2850)
SUBSIDY_BETWEEN_2024_2025 = float(2925)
SUBSIDY_BETWEEN_2025_PLUS = float(2350)


class HSWebhook:
    API_KEY = "hubspot-token"
    PIPELINE_TYPE = {
        'default': 'ONE',
        '350385367': 'TWO',
        '350385364': 'THREE',
        '39929315': 'FOUR',
    }
    class ennumType():
        ONE = "ONE"
        TWO = "TWO"
        THREE = "THREE"
        FOUR = "FOUR"

    class ennumManufacturor():
        ON = "ON", "On"
        OFF = "OFF", "Off"
        TRIAL = "TRIAL", "Trial"


    def __init__(self, deal_id):
        self.deal_id = deal_id
        self.hubspot_client = hubspot.Client.create(access_token=self.API_KEY)
        self.deal = self.get_deal()
        self.contact_id = self.get_contact_id()
        self.customer_contact_info = {}
        self.products = []
        self.line_item_ids = self.get_deal_line_items()
        self.fetch_contact()
        self.get_products()
        self.get_all_attributes()
        
        self.total_line_items()
        print('installation info:', self.installation_information)
        print('contact info:', self.customer_contact_info)
        print('address:', self.contact_address)
        print('quantity:', self.quantity)
        print('line_items_id:', self.line_item_ids)
        print("products", self.products)

    def get_products(self):
        if self.deal:
            print("deal properties", self.deal.properties)

            
            self.device_type =  self.PIPELINE_TYPE.get(self.deal.properties.get("pipeline", ''), None)
            manucaturor_active = self.deal.properties.get("manucaturor_active", self.ennumType.ONE)
                
            if self.device_type == self.ennumType.ONE:
                product = {
                    "name": self.deal.properties.get("product_name", None),
                    "type": self.ennumType.ONE,
                    "manucaturor": self.ennumManufacturor.ON if manucaturor_active else self.ennumManufacturor.OFF,
                        #price
                }
                dwe_product = {
                    "name": self.deal.properties.get("product_name", None) ,
                    "type": self.ennumType.THREE,
                    "manucaturor": self.ennumManufacturor.OFF,
                        #price
                }
                self.products.append(product)
                self.products.append(dwe_product)

            elif self.device_type == self.ennumType.FOUR:
                product = {
                    "name": self.deal.properties.get("product_name", None),
                    "type": self.ennumType.FOUR,
                    "manucaturor": self.ennumManufacturor.OFF,
                        #price
                }
                self.products.append(product)

            elif self.device_type == self.ennumType.TWO:
                product_pt = {
                    "name": self.deal.properties.get("product_name", None),
                    "type": self.ennumType.TWO,
                    "manucaturor": self.ennumManufacturor.OFF,
                        #price
                }
                self.products.append(product_pt)

            elif self.device_type == self.PIPELINE_TYPE['350385364']:
                product_dwe = {
                    "name": self.deal.properties.get("product_name", None),
                    "type": self.ennumType.THREE,
                    "manucaturor": self.ennumManufacturor.OFF,
                        #price
                }
                product_pt = {
                    "name": self.deal.properties.get("product_name", None)+ '_T',
                    "type": self.ennumType.TWO,
                    "manucaturor": self.ennumManufacturor.OFF,
                        #price
                }
                product = {
                    "name": self.deal.properties.get("product_name", None),
                    "type": self.ennumType.ONE,
                    "manucaturor": self.ennumManufacturor.ON if manucaturor_active else self.ennumManufacturor.OFF,
                        #price
                }
                self.products.append(product)
                self.products.append(product_pt)
                self.products.append(product_dwe)
                
    
    def get_all_attributes(self):
            create_date = self.deal.properties.get('createdate', '')
            self.created_at = datetime.datetime.strptime(create_date[:10], "%Y-%m-%d") if create_date else datetime.datetime.now()
            self.first_installation_day = datetime.datetime.strptime(self.deal.properties.get('first_installation_day'), "%Y-%m-%d") if self.deal.properties.get('first_installation_day', None) else datetime.datetime.now()
            self.contact_address = {
                'street': self.deal.properties.get('customer_address', ''),
                'zip_code': self.deal.properties.get('customer_postcode', ''),
                'city': self.deal.properties.get('customer_city', ''),
                'g_maps_link': self.deal.properties.get('google_maps_link', ''),
            }

            self.quantity = self.deal.properties.get('customer_product_quantity', '')
            team, pickup_location = self.deal.properties.get('pick_up_location','').split('-', 1)
            self.installation_information = {
                'first_installation_day': self.first_installation_day,
                'second_installation_date': self.deal.properties.get('second_installation_date', ''),
                'work_preparation_by': self.deal.properties.get('responsible_for_work_preparation_', ''),
                'work_preparation_note': self.deal.properties.get('notes_work_preparation', ''),
                'team': team,
                'team_pick_up_location': pickup_location
            }


    def get_deal(self):
        try:
            return self.hubspot_client.crm.deals.basic_api.get_by_id(self.deal_id,
                                                                    properties= ['product_name','pipeline','manucaturor_active','amount', 'customer_product_quantity'
                                                                                 'customer_city','customer_postcode','customer_address','google_maps_link',
                                                                                 'dealstage','installation_day', 'location']
                                                                     )
        except DealApiException as e:
            print(f"Failed to fetch deal: {e}")
            return None

    def get_contact_id(self):
        try:
            batch_request = BatchInputPublicFetchAssociationsBatchRequest(inputs=[{"id": self.deal_id}])

            response = self.hubspot_client.crm.associations.v4.batch_api.get_page(
                batch_input_public_fetch_associations_batch_request=batch_request,
                from_object_type="deals",
                to_object_type="contacts",
            )
            if response.results:
                return response.results[0].to[0].to_object_id
            else: 
                return None
            
        except AssociationApiException:
            return None
        
    def fetch_contact(self):
        if self.contact_id:
            try:
                contact = self.hubspot_client.crm.contacts.basic_api.get_by_id(contact_id=self.contact_id,
                                                                               properties=["firstname", "lastname","phone","email"]
                                                                               )
                if contact:
                    print("contact props:", contact.properties)
                    self.customer_contact_info.update({
                        "first_name": contact.properties.get('firstname', ''),
                        "last_name": contact.properties.get('lastname', ''),
                        "email": contact.properties.get('email', ''),
                        "phone": contact.properties.get('phone', '')
                    })
                    print("Updated contact info from CRM:", self.customer_contact_info)
                else:
                    print("contact not found")
            except ContactApiException as e:
                print(f"Failed to fetch contact details: {e}")

    def get_deal_line_items(self):
        line_item_ids = []
        try:
            batch_request = BatchInputPublicFetchAssociationsBatchRequest(inputs=[{"id": self.deal_id}])

            response = self.hubspot_client.crm.associations.v4.batch_api.get_page(
                batch_input_public_fetch_associations_batch_request=batch_request,
                from_object_type="deals",
                to_object_type="line_items",
            )
            if response.results:
                print("line item resluts", response.results)
                for result in response.results:
                    association_types = result.to
                    for association in association_types:
                        line_item_ids.append(association.to_object_id)

            return line_item_ids
        except LineItemApiException:
            return []

    def get_item_line_by_id(self, item_id):
        properties = {
            "id": item_id,
        }
        try:
            api_response = self.hubspot_client.crm.line_items.basic_api.get_by_id(
                line_item_id=item_id, properties=["name", "amount", "quantity"]
            )
            props = api_response.properties
            properties["name"] = props["name"]
            properties["amount"] = float(props.get("amount", 0))
            properties["quantity"] = int(props.get("quantity", 1))
            return properties
        except LineItemApiException:
            return None

    def get_subsidy_value(self,type):
        if type == self.ennumType.TWO:
            return POMP_T_SUBSIDY

        if self.first_installation_day.date() < datetime.date(2024, 1, 1):
            return SUBSIDY_BEFORE_2024
        elif self.first_installation_day.date() < datetime.date(2025, 1, 1):
            return SUBSIDY_BETWEEN_2024_2025
        elif self.created_at.year == 2024 and self.first_installation_day.year == 2025:
            return SUBSIDY_BETWEEN_2024_2025
        return SUBSIDY_BETWEEN_2025_PLUS

    def total_line_items(self):
        
        price = 0
        pt_price = 0
        dwe_price = 0
        ao_price = 0
        print("self device_type: ", self.device_type)
        for item in self.line_item_ids:
            line_item_properties = self.get_item_line_by_id(item)
            print("self line items: ", line_item_properties)
            if self.device_type != self.PIPELINE_TYPE["350385364"] and self.device_type != self.ennumType.ONE:
                price += line_item_properties['amount']
            else:
                if "Pomp T" in line_item_properties["name"]:
                    pt_price += line_item_properties['amount']
                elif "Element" in line_item_properties["name"] or "Dewarmte Element" in line_item_properties["name"]:
                    dwe_price += line_item_properties['amount']
                else:
                    ao_price += line_item_properties["amount"]
        if self.device_type != self.PIPELINE_TYPE["350385364"] and self.device_type != self.ennumType.ONE:
            print("net price: ", price)
            subsidy = self.get_subsidy_value(self.device_type)
            self.products[0].update({"price": round(price - subsidy, 2)})
        else:
            for product in self.products:
                if product["type"] == self.ennumType.ONE:
                    if ao_price == 0:
                        self.products.remove(product)
                    else:
                        subsidy = self.get_subsidy_value()
                        product.update({"price": round(ao_price - subsidy, 2)})
                elif product["type"] == self.ennumType.TWO:
                    if pt_price == 0:
                        self.products.remove(product)
                    else:
                        subsidy = self.get_subsidy_value(type=self.ennumType.TWO)
                        product.update({"price": round(pt_price - subsidy,2)})
                elif product["type"] == self.ennumType.THREE:
                    if dwe_price == 0:
                        self.products.remove(product)
                    else:
                        subsidy = self.get_subsidy_value(type=self.ennumType.THREE)
                        product.update({"price": round(dwe_price - subsidy ,2)})



