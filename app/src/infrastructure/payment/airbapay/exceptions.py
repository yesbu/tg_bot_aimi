class AirbaPayException(Exception):
    def __init__(self, message: str, code: int | None = None, status: str | None = None):
        self.message = message
        self.code = code
        self.status = status
        super().__init__(self.message)


class AirbaPayAuthException(AirbaPayException):
    pass


class AirbaPayPaymentException(AirbaPayException):
    pass


class AirbaPayRefundException(AirbaPayException):
    pass


class AirbaPayNetworkException(AirbaPayException):
    pass
