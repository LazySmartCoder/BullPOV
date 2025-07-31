# import requests
# import json
# cashfree_apikey = "1032514dc2c30325fe7444306234152301"
# cashfree_sk = "cfsk_ma_prod_96165f356ad185da70efc4d959eb5375_75b7f4a3"
# # ✅ Use your Production credentials here
# XClientId = cashfree_apikey
# XClientSecret = cashfree_sk

# # ✅ Use production URL
# url = "https://api.cashfree.com/pg/links"

# # Headers
# headers = {
#     "Content-Type": "application/json",
#     "x-api-version": "2022-09-01",
#     "x-client-id": XClientId,
#     "x-client-secret": XClientSecret
# }

# # Payment link data
# data = {
#     "customer_details": {
#         "customer_id": "cust001",
#         "customer_email": "test@example.com",
#         "customer_phone": "9740168962"
#     },
#     "link_notify": {
#         "send_sms": True,
#         "send_email": True
#     },
#     "link_meta": {
#         "return_url": "https://yourdomain.com/payment/return"
#     },
#     "link_amount": 199.00,
#     "link_currency": "INR",
#     "link_purpose": "Test Payment"
# }

# # Make the request
# response = requests.post(url, headers=headers, data=json.dumps(data))

# # Print the response
# print("Status Code:", response.status_code)
# print("Response:", response.text)


import requests

url = "https://api.cashfree.com/pg/links"

payload = {
    "link_id": "ghtryh",
    "link_amount": 10,
    "link_currency": "INR",
    "link_purpose": "fees",
    "customer_details": { "customer_phone": "9740168962" }
}
headers = {
    "x-client-id": "1032514dc2c30325fe7444306234152301",
    "x-client-secret": "cfsk_ma_prod_5976d2eeb14ad82fc05be1f5ba5280b3_286c1636",
    "x-api-version": "2022-09-01",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())
