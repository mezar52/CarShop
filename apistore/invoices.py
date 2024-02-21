import base64
import hashlib

import ecdsa
import requests

from store.models import Order
from django.conf import settings


def verify_signature(request):
    pub_key_base64 = "LS0tLS1CRUdJTiBQVUJMSUMgS0VZLS0tLS0KTUZrd0V3WUhLb1pJemowQ0FRWUlLb1pJemowREFRY0RRZ0FFc05mWXpNR1hIM2VXVHkzWnFuVzVrM3luVG5CYgpnc3pXWnhkOStObEtveDUzbUZEVTJONmU0RlBaWmsvQmhqamgwdTljZjVFL3JQaU1EQnJpajJFR1h3PT0KLS0tLS1FTkQgUFVCTElDIEtFWS0tLS0tCg=="
    x_sign_base64 = request.headers["X-Sign"]

    body_bytes = request.body
    print(body_bytes)
    pub_key_bytes = base64.b64decode(pub_key_base64)
    signature_bytes = base64.b64decode(x_sign_base64)
    pub_key = ecdsa.VerifyingKey.from_pem(pub_key_bytes.decode())

    ok = pub_key.verify(
        signature_bytes,
        body_bytes,
        sigdecode=ecdsa.util.sigdecode_der,
        hashfunc=hashlib.sha256,
    )
    if not ok:
        raise Exception("Signature is not valid")


def create_invoice(order: Order, webhook_url):
    amount = 0
    basket_order = []
    for qty in order.car_types.all():
        sum_ = (qty.car_type.price * qty.quantity) * 100
        amount += sum_
        basket_order.append(
            {
                "name": qty.car_type.name,
                "qty": qty.quantity,
                "sum": sum_,
            }
        )

    merchants_info = {
        "reference": str(order.id),
        "destination": "Buying cars",
        "basketOrder": basket_order,
    }
    request_body = {
        "webHookUrl": webhook_url,
        "amount": amount,
        "merchantPaymInfo": merchants_info,
    }
    headers = {"X-Token": settings.MONOBANK_TOKEN}

    request = requests.post(
        "https://api.monobank.ua/api/merchant/invoice/create",
        json=request_body,
        headers=headers,
    )
    request.raise_for_status()
    order.order_id = request.json()["invoiceId"]
    order.invoice_url = request.json()["pageUrl"]
    order.status = "created"
    order.save()
