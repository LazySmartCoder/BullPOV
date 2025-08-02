def refund_payment(order_id, refund_amount, refund_note="Refund initiated due to user error in payment."):
    url = f"https://api.cashfree.com/pg/orders/{order_id}/refunds"
    headers = {
        "x-client-id": "1032514dc2c30325fe7444306234152301",
        "x-client-secret": "cfsk_ma_prod_5976d2eeb14ad82fc05be1f5ba5280b3_286c1636",
        "x-api-version": "2025-01-01",
        "Content-Type": "application/json"
    }
    payload = {
        "refund_amount": refund_amount,
        "refund_note": refund_note,
        "refund_id": f"refund_{uuid.uuid4().hex[:8]}"
    }
    resp = requests.post(url, headers=headers, json=payload)
    return resp.status_code, resp.json()

@csrf_exempt
@require_POST
def cashfree_webhook(request):
    if request.method == "POST":
        try:
            payload = json.loads(request.body)
            
            data = payload.get("data", {})
            order = data.get("order", {})

            customer_details = order.get("customer_details", {})
            customer_name = customer_details.get("customer_name")
            customer_email = customer_details.get("customer_email")
            customer_phone = customer_details.get("customer_phone")
            order_id = order.get("order_id")
            order_amount = order.get("order_amount")
            payment_status = order.get("order_status")
            txn = WalletTxn.objects.filter(LoggedINEmail = customer_email).last()

            user = User.objects.get(email = customer_email)
            if payment_status == "PAID":
                if txn.LoggedINEmail == customer_email:
                    userdet = UserDetail.objects.get(User = user)
                    userdet.WalletBalance = userdet.WalletBalance + float(order_amount)
                    userdet.PhoneNumber = customer_phone
                    userdet.save()
                    txn.Amount = order_amount
                    txn.Action = True
                    txn.OrderID = order_id
                    txn.TxnID = payload['data']['order']['transaction_id']
                    txn.Status = "SUCCESS"
                    txn.save()
                    sendEmail("no-reply@bullpov.com", user.email, "Money Successfully Deposited to Your BullPOV Account!", normal_text_templates(user.first_name, f"Great news! Your deposit has been successfully credited to your BullPOV wallet. <br><br>Deposited Amount: ₹{order_amount}<br>Current Balance: ₹{float(round(int(userdet.WalletBalance), 2))}<br><br>You can now use this amount to place trades on BullPOV. Happy Trading!"))
                else:
                    refund_payment(order_id, order_amount)
                    sendEmail("no-reply@bullpov.com", user.email, "Refund Initiated for Your Mistaken Transaction", normal_text_templates(user.first_name, f"We noticed a mismatch in your recent transaction with us. Please don’t worry, we've already initiated a refund for the full amount you paid. The refund should reflect in your bank account or original payment method within 5–7 business days, depending on your bank or payment provider. <br>If you have any questions or need further assistance, feel free to reply to this email or reach out to our support team."))
            else:
                return JsonResponse({"message": "Payment not successful"}, status=400)

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)