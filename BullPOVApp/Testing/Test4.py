import requests

url = "https://api.cashfree.com/pg/links"

payload = {
    "link_amount": 9,
    "customer_details": { "customer_phone": "6355853038" },
    "link_currency": "INR",
    "link_purpose": "fees",
    "link_id": "hi7"
}
headers = {
    "x-client-id": "1032514dc2c30325fe7444306234152301",
    "x-client-secret": "cfsk_ma_prod_5976d2eeb14ad82fc05be1f5ba5280b3_286c1636",
    "x-api-version": "2025-01-01",
    "Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())