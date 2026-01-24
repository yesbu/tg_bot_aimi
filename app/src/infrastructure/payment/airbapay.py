import httpx
from src.infrastructure.payment.operations.payment import AirbaPayPaymentGateway
from src.infrastructure.payment.operations.payout import AirbaPayPayoutGateway
from src.infrastructure.payment.operations.subscription import AirbaPaySubscriptionGateway
from src.infrastructure.payment.operations.card import AirbaPayCardGateway
from src.infrastructure.payment.operations.webhook import AirbaPayWebhookGateway


class AirbaPayGateway:
    def __init__(
        self,
        user: str,
        password: str,
        terminal_id: str,
        client: httpx.AsyncClient,
        timeout: float = 30.0,
    ):
        self._user = user
        self._password = password
        self._terminal_id = terminal_id
        self._timeout = timeout
        self._client = client


    @property
    def payment(self) -> AirbaPayPaymentGateway:
        return AirbaPayPaymentGateway(
            client=self._client,
            user = self._user,
            password = self._password,
            terminal_id = self._terminal_id,
        )

    @property
    def card(self) -> AirbaPayCardGateway:
        return AirbaPayCardGateway(
            client=self._client,
            user = self._user,
            password = self._password,
            terminal_id = self._terminal_id,
        )

    # not tested
    @property
    def payout(self) -> AirbaPayPayoutGateway:
        return AirbaPayPayoutGateway(
            client=self._client,
            user = self._user,
            password = self._password,
            terminal_id = self._terminal_id,
        )
    
    # not tested
    @property
    def subscription(self) -> AirbaPaySubscriptionGateway:
        return AirbaPaySubscriptionGateway(
            client=self._client,
            user = self._user,
            password = self._password,
            terminal_id = self._terminal_id,
        )
    
    # not tested
    @property
    def webhook(self) -> AirbaPayWebhookGateway:
        return AirbaPayWebhookGateway(
            client=self._client,
            user = self._user,
            password = self._password,
            terminal_id = self._terminal_id,
        )

    async def close(self):
        await self._client.aclose()


