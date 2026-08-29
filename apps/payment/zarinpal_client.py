import requests

from django.conf import settings


class ZarinPal:

    payment_request_url = "https://sandbox.zarinpal.com/pg/v4/payment/request.json"

    payment_verify_url = "https://sandbox.zarinpal.com/pg/v4/payment/verify.json"

    payment_start_url = "https://sandbox.zarinpal.com/pg/StartPay/"

    def __init__(self):
        self.merchant_id = settings.MERCHANT_ID

    def _headers(self):
        return {
            "accept": "application/json",
            "content-type": "application/json",
        }

    def payment_request(
        self,
        amount,
        callback_url,
        description="پرداختی کاربر",
        mobile=None,
        email=None,
        order_id=None,
    ):
        metadata = {}

        if mobile:
            metadata["mobile"] = str(mobile)

        if email:
            metadata["email"] = str(email)

        if order_id:
            metadata["order_id"] = str(order_id)

        data = {
            "merchant_id": self.merchant_id,
            "amount": int(amount),
            "callback_url": callback_url,
            "description": description,
            "metadata": metadata,
        }

        response = requests.post(
            self.payment_request_url,
            json=data,
            headers=self._headers(),
            timeout=400,
        )

        print("ZARINPAL REQUEST:", data)
        print("ZARINPAL STATUS:", response.status_code)
        print("ZARINPAL RESPONSE:", response.text)

        try:
            result = response.json()
        except ValueError:
            response.raise_for_status()
            raise Exception("Invalid response from ZarinPal")

        if response.status_code != 200:
            raise Exception(
                f"ZarinPal error: " f"{result.get('errors', result.get('data', {}))}"
            )

        code = result.get("data", {}).get("code")

        if code != 100:
            raise Exception(
                result.get("data", {}).get(
                    "message",
                    "Payment request failed",
                )
            )

        return result["data"]["authority"]

    def payment_verify(
        self,
        amount,
        authority,
    ):
        data = {
            "merchant_id": self.merchant_id,
            "amount": int(amount),
            "authority": authority,
        }

        response = requests.post(
            self.payment_verify_url,
            json=data,
            headers=self._headers(),
            timeout=400,
        )

        print("ZARINPAL VERIFY REQUEST:", data)
        print(
            "ZARINPAL VERIFY STATUS:",
            response.status_code,
        )
        print(
            "ZARINPAL VERIFY RESPONSE:",
            response.text,
        )

        try:
            result = response.json()
        except ValueError:
            response.raise_for_status()
            raise Exception("Invalid response from ZarinPal")

        if response.status_code != 200:
            error_message = (
                result.get("errors")
                or result.get("data", {}).get("message")
                or "ZarinPal verification failed"
            )

            raise Exception(f"ZarinPal error: {error_message}")

        return result

    def generate_payment_url(
        self,
        authority,
    ):
        return f"{self.payment_start_url}" f"{authority}"
