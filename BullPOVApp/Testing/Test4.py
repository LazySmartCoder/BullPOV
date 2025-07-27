import requests
import random

def send_whatsapp_otp_via_fast2sms(phone_number, api_url):
    """
    phone_number: str, including country code (e.g., '919812345678')
    api_url: base API URL from Fast2SMS with placeholders for OTP and number
    """
    otp = str(random.randint(100000, 999999))
    url = api_url.format(phone_number=phone_number, otp=otp)

    resp = requests.get(url)
    print("Status code:", resp.status_code)
    print("Response:", resp.text)
    return otp

# Example usage:
# Replace api_url with the one Fast2SMS provides (example format shown)
api_url = (
    "https://fast2sms.com/whatsapp/otp?"
    "apikey=fVj1IFml7HnhyO9NcYqCaQLziRbodZkUXx2P8w6gMvTS40puWDVOutxaWR9pHvJerk7D5hCgyqB4KfIb&"
    "mobile_number={phone_number}&"
    "message_id=YOUR_TEMPLATE_ID&"
    "variables_values={otp}"
)

sent_otp = send_whatsapp_otp_via_fast2sms("+916355853038", api_url)
print("OTP sent:", sent_otp)
