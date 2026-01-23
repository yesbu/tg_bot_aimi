import httpx
from loguru import logger
from typing import Any, Optional
from dataclasses import dataclass
from datetime import datetime   


class AirbaPayPaymentGateway:
    def __init__(
        self,
        client: httpx.AsyncClient,
        user: str,
        password: str,
        terminal_id: str,
        timeout: float = 30.0,
    ):
        self._client = client
        self._user = user
        self._password = password
        self._terminal_id = terminal_id
        self._timeout = timeout

    async def _get_token(self, payment_id: str = None) -> str:
        payload = {
            "user": self._user,
            "password": self._password,
            "terminal_id": self._terminal_id,
        }

        if payment_id:
            payload["payment_id"] = payment_id

        try:
            response = await self._client.post(
                "/api/v1/auth/sign-in",
                json=payload,
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            token = data.get("access_token")

            if not token:
                raise ValueError("No access_token in response")

            logger.debug("Successfully authenticated with AirbaPay")
            return token

        except httpx.HTTPStatusError as e:
            logger.error(f"AirbaPay auth failed: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            logger.error(f"AirbaPay auth error: {e}")
            raise

    def _get_auth_headers(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}
    
    async def create_payment(
        self,
        invoice_id: str,
        amount: float,
        account_id: str,
        render_apple_pay: bool,
        render_google_pay: bool,
        currency: str = "KZT",
        language: str = "ru",

        auto_charge: Optional[int] = 1,
        card_save: Optional[bool] = False,
        phone: Optional[str] = None,
        email: Optional[str] = None,
        description: Optional[str] = None,
        success_callback: Optional[str] = None,
        failure_callback: Optional[str] = None,
        success_back_url: Optional[str] = None,
        failure_back_url: Optional[str] = None,


    ) -> dict[str, Any]:
        token = await self._get_token()

        payload: dict[str, Any] = {
            "invoice_id": invoice_id,
            "amount": amount,
            "currency": currency,
            "description": description,
            "auto_charge": auto_charge,
            "card_save": card_save,
            "account_id": account_id,
            "phone": phone,
            "email": email,
            "language": language,
            "failure_back_url": failure_back_url,
            "success_back_url": success_back_url,
            "success_callback": success_callback,
            "failure_callback": failure_callback,
            "add_parameters": {
                "payform":{
                    "render_apple_pay": render_apple_pay,
                    "render_google_pay": render_google_pay,
                    "render_save_cards": True,
                    "request_cvv": False,
                }
            },
        }

        try:
            response = await self._client.post(
                "/api/v2/payments/",
                json=payload,
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Payment created: invoice_id={invoice_id}, payment_id={data.get('id')}")

            return {
                "success": True,
                "payment_id": data.get("id"),
                "invoice_id": data.get("invoice_id"),
                "redirect_url": data.get("redirect_url"),
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Create payment failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Create payment error: {e}")
            return {"success": False, "error": str(e)}


    async def get_payment_status(self, payment_id: str) -> dict[str, Any]:
        token = await self._get_token(payment_id)

        try:
            response = await self._client.get(
                "/api/v1/payments",
                params={"id": payment_id},
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Payment status retrieved: payment_id={payment_id}")

            return {
                "success": True,
                "data": data,
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Get payment status failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Get payment status error: {e}")
            return {"success": False, "error": str(e)}

    async def refund_payment(
        self,
        payment_id: str,
        ext_id: str | None = None,
        amount: float | None = None,
        reason: str | None = None,
    ) -> dict[str, Any]:
        token = await self._get_token(payment_id=payment_id)

        payload: dict[str, Any] = {
            "payment_id": payment_id,
        }

        try:
            response = await self._client.request(
                "DELETE",
                f"/api/v1/payments/return",
                json=payload,
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Refund processed: payment_id={payment_id}, refund_id={data.get('id')}")

            return {
                "success": True,
                "data": data,
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Refund failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Refund error: {e}")
            return {"success": False, "error": str(e)}

    # Метод для заморзки денег и потом спишеться, auto_charge=0
    async def charge(
        self,
        payment_id: str,
        amount: float | None = None,
    ) -> dict[str, Any]:
        token = await self._get_token()

        payload: dict[str, Any] = {}
        if amount is not None:
            payload["amount"] = amount

        try:
            response = await self._client.put(
                f"/api/v1/payments/charge",
                json=payload if payload else None,
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Payment charged: payment_id={payment_id}")

            return {
                "success": True,
                "payment_id": data.get("id"),
                "status": data.get("status"),
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Charge failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Charge error: {e}")
            return {"success": False, "error": str(e)}

 


