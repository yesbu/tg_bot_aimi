import httpx
from loguru import logger
from typing import Any, Optional
from dataclasses import dataclass
from datetime import datetime   




class AirbaPayPayoutGateway:
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

    async def _get_token(self, payout_id: str = None) -> str:
        payload = {
            "user": self._user,
            "password": self._password,
            "terminal_id": self._terminal_id,
        }

        if payout_id:
            payload["payout_id"] = payout_id

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

    # 500 ошибка сервера
    async def calculate_fee(
        self,
        amount: float,
        currency: str = "KZT",
    ) -> dict[str, Any]:
        token = await self._get_token()

        payload: dict[str, Any] = {
            "amount": amount,
            "currency": currency,
        }

        try:
            response = await self._client.post(
                "/api/v1/payouts/calculate-fee",
                json=payload,
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Fee calculated for amount={amount}")

            return {
                "success": True,
                "data": data,
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Calculate fee failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Calculate fee error: {e}")
            return {"success": False, "error": str(e)}

    # 404 ошибка
    async def create_payout(
        self,
        account_id: str,
        amount: float,
        currency: str = "KZT",
        invoice_id: str | None = None,
        purpose: str | None = None,
        iin: str | None = None,
        email: str | None = None,
        phone: str | None = None,
        code_purpose: str | None = None,
        failure_back_url: str | None = None,
        success_back_url: str | None = None,
        success_callback: str | None = None,
        failure_callback: str | None = None
    ) -> dict[str, Any]:
        token = await self._get_token()

        payload: dict[str, Any] = {
            "account_id": account_id,
            "amount": amount,
            "currency": currency,
            "invoice_id": invoice_id,
            "purpose": purpose,
            "iin": iin,
            "email": email,
            "phone": phone,
            "code_purpose": code_purpose,
            "failure_back_url": failure_back_url,
            "success_back_url": success_back_url,
            "success_callback": success_callback,
            "failure_callback": failure_callback,
        }

        try:
            response = await self._client.post(
                "/api/v1/payout",
                json=payload,
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            logger.info(f"Payout created: invoice_id={invoice_id}, payout_id={data.get('id')}")

            return {
                "success": True,
                "data": data,
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Create payout failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Create payout error: {e}")
            return {"success": False, "error": str(e)}

    async def process_payout(self, card_id: str) -> dict[str, Any]:
        token = await self._get_token()

        try:
            response = await self._client.post(
                f"/api/v1/payouts/process/{card_id}",
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            logger.info(f"Payout processed: payout_id={card_id}")

            return {"success": True}

        except httpx.HTTPStatusError as e:
            logger.error(f"Process payout failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Process payout error: {e}")
            return {"success": False, "error": str(e)}

    async def get_payout_status(self, payout_id: str) -> dict[str, Any]:
        token = await self._get_token()

        try:
            response = await self._client.get(
                f"/api/v1/payouts",
                headers=self._get_auth_headers(token),
                timeout=self._timeout,
            )
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Payout status retrieved: payout_id={payout_id}")

            return {
                "success": True,
                "data": data,
            }

        except httpx.HTTPStatusError as e:
            logger.error(f"Get payout status failed: {e.response.status_code} - {e.response.text}")
            return {
                "success": False,
                "error": e.response.text,
                "status_code": e.response.status_code,
            }
        except Exception as e:
            logger.error(f"Get payout status error: {e}")
            return {"success": False, "error": str(e)}
