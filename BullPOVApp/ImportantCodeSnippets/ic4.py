from cashfree_pg.api_client import Cashfree

Cashfree.XClientId = "1032514dc2c30325fe7444306234152301"
Cashfree.XClientSecret = "cfsk_ma_prod_96165f356ad185da70efc4d959eb5375_75b7f4a3"
Cashfree.XEnvironment = Cashfree.PRODUCTION
x_api_version = "2025-01-01"

try:
    api_response = Cashfree().PGOrderFetchPayments(x_api_version, "devstudio_7356450000799365957", None)
    print(api_response.data)
except Exception as e:
    print(e)