from typing import Any
from datetime import datetime
import httpx
from loguru import logger

from src.application.interfaces.payment import IPaymentGateway
from src.infrastructure.payment.airbapay.types import (
    AirbaAuthResponse,
    AirbaPaymentResponse,
    AirbaPaymentStatusResponse,
    AirbaRefundResponse,
    AirbaRefund,
    AirbaErrorResponse,
)
from src.infrastructure.payment.airbapay.enums import (
    AirbaLanguage,
    AirbaAutoCharge,
)
from src.infrastructure.payment.airbapay.exceptions import (
    AirbaPayAuthException,
    AirbaPayPaymentException,
    AirbaPayRefundException,
    AirbaPayNetworkException,
)


class AirbaPayClient(IPaymentGateway):
    BASE_URL = "https://ps.airbapay.kz/acquiring-api"
    
    def __init__(
        self,
        username: str,
        password: str,
        terminal_id: str,
        timeout: int = 30,
    ):
        self._username = username
        self._password = password
        self._terminal_id = terminal_id
        self._timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)
        self._token: str | None = None
        self._token_expires_at: datetime | None = None
    
    async def _get_token(self) -> str:
        if self._token and self._token_expires_at:
            if datetime.utcnow() < self._token_expires_at:
                return self._token
        
        logger.info("Authenticating with AirbaPay")
        
        try:
            response = await self._client.post(
                f"{self.BASE_URL}/api/v1/auth/sign-in",
                json={
                    "user": self._username,
                    "password": self._password,
                    "terminal_id": self._terminal_id,
                }
            )
            
            if response.status_code != 200:
                error_data = response.json().get("error", {})
                raise AirbaPayAuthException(
                    message=error_data.get("message", "Authentication failed"),
                    code=error_data.get("code"),
                    status=error_data.get("status"),
                )
            
            data = response.json()
            self._token = data.get("token")
            
            logger.info("Successfully authenticated with AirbaPay")
            return self._token
            
        except httpx.HTTPError as e:
            logger.error(f"Network error during authentication: {e}")
            raise AirbaPayNetworkException(f"Network error: {str(e)}")
    
    async def _make_request(
        self,
        method: str,
        endpoint: str,
        data: dict[str, Any] | None = None,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        token = await self._get_token()
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            response = await self._client.request(
                method=method,
                url=url,
                json=data,
                params=params,
                headers=headers,
            )
            
            if response.status_code in [400, 401, 403, 404, 500]:
                error_data = response.json().get("error", {})
                raise AirbaPayPaymentException(
                    message=error_data.get("message", "Request failed"),
                    code=error_data.get("code", response.status_code),
                    status=error_data.get("status", response.reason_phrase),
                )
            
            return response.json()
            
        except httpx.HTTPError as e:
            logger.error(f"Network error during request: {e}")
            raise AirbaPayNetworkException(f"Network error: {str(e)}")
    
    async def create_payment(
        self,
        invoice_id: str,
        amount: float,
        currency: str,
        account_id: str,
        phone: str | None = None,
        email: str | None = None,
        description: str | None = None,
        success_callback: str | None = None,
        failure_callback: str | None = None,
        auto_charge: bool = True,
        card_save: bool = False,
        language: str = "ru",
        success_back_url: str | None = None,
        failure_back_url: str | None = None,
    ) -> dict[str, Any]:
        logger.info(f"Creating payment: invoice_id={invoice_id}, amount={amount}")
        
        payload = {
            "invoice_id": invoice_id,
            "amount": amount,
            "currency": currency,
            "account_id": account_id,
            "auto_charge": AirbaAutoCharge.ONE_STAGE if auto_charge else AirbaAutoCharge.TWO_STAGE,
            "card_save": card_save,
            "language": language,
        }
        
        if phone:
            payload["phone"] = phone
        if email:
            payload["email"] = email
        if description:
            payload["description"] = description
        if success_callback:
            payload["success_callback"] = success_callback
        if failure_callback:
            payload["failure_callback"] = failure_callback
        if success_back_url:
            payload["success_back_url"] = success_back_url
        if failure_back_url:
            payload["failure_back_url"] = failure_back_url
        
        response_data = await self._make_request(
            method="POST",
            endpoint="/api/v2/payments/",
            data=payload,
        )
        
        logger.info(f"Payment created: payment_id={response_data.get('id')}")
        return response_data
    
    async def get_payment_status(self, payment_id: str) -> dict[str, Any]:
        logger.info(f"Getting payment status: payment_id={payment_id}")
        
        response_data = await self._make_request(
            method="GET",
            endpoint=f"/api/v1/payments/{payment_id}",
        )
        
        logger.info(f"Payment status: {response_data.get('status')}")
        return response_data
    
    async def refund_payment(
        self,
        payment_id: str,
        amount: float | None = None,
        reason: str | None = None,
        ext_id: str | None = None,
    ) -> dict[str, Any]:
        logger.info(f"Refunding payment: payment_id={payment_id}, amount={amount}")
        
        payload = {}
        
        if ext_id:
            payload["ext_id"] = ext_id
        if amount is not None:
            payload["amount"] = amount
        if reason:
            payload["reason"] = reason
        
        response_data = await self._make_request(
            method="DELETE",
            endpoint=f"/api/v1/payments/{payment_id}/return",
            data=payload,
        )
        
        logger.info(f"Refund created: refund_id={response_data.get('id')}")
        return response_data
    
    async def close(self) -> None:
        logger.info("Closing AirbaPay client")
        await self._client.aclose()
