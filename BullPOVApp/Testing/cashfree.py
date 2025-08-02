# import requests

# url = "https://api.cashfree.com/pg/links"

# payload = {
#     "link_id": "543",
#     "link_amount": 10,
#     "link_currency": "INR",
#     "link_purpose": "Wallet Deposit",
#     "customer_details": { "customer_phone": "6355853038" }
# }
# headers = {
#     "x-client-id": "1032514dc2c30325fe7444306234152301",
#     "x-client-secret": "cfsk_ma_prod_c7c76f38c9ef7134f84ba1df857e0874_e16973e8",
#     "x-api-version": "2025-01-01",
#     "Content-Type": "application/json"
# }

# response = requests.post(url, json=payload, headers=headers)

# print(response.json())

from cashfree_pg.models.create_order_request import CreateOrderRequest
from cashfree_pg.api_client import Cashfree
from cashfree_pg.models.customer_details import CustomerDetails


Cashfree.XClientId = "1032514dc2c30325fe7444306234152301"
Cashfree.XClientSecret = "cfsk_ma_prod_c7c76f38c9ef7134f84ba1df857e0874_e16973e8"
Cashfree.XEnvironment = Cashfree.PRODUCTION
x_api_version = "2023-08-01"

def create_order():
        customerDetails = CustomerDetails(customer_id="123", customer_phone="6355853038")
        createOrderRequest = CreateOrderRequest(order_amount=10, order_currency="INR", customer_details=customerDetails)
        try:
            api_response = Cashfree().PGCreateOrder(x_api_version, createOrderRequest, None, None)
            print(api_response.data)
        except Exception as e:
            print(e)
create_order()