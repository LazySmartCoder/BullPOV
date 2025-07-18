import razorpay

# Initialize Razorpay client
client = razorpay.Client(auth=("rzp_test_YjhKDgUp7UCeRe", "TwuPT0bP0PO5Ltn5OYlU0qAN"))

# Create a new order
def create_order(amount_in_rupees, receipt_id="order_rcptid_11"):
    amount_in_paisa = int(amount_in_rupees * 100)  # Razorpay accepts amount in paisa
    order_data = {
        "amount": amount_in_paisa,
        "currency": "INR",
        "receipt": receipt_id,
        "payment_capture": 1  # Auto capture
    }

    order = client.order.create(data=order_data)
    return order

# Usage
order = create_order(500.0)  # ₹500
print("Order ID:", order['id'])
print("Order Details:", order)
