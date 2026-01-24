from enum import StrEnum, IntEnum


class PaymentStatusEnum(StrEnum):
    NEW = "new"
    SECURE_3D = "secure3D"
    AUTH = "auth"
    SUCCESS = "success"
    ERROR = "error"
    RETURN = "return"
    REFUND = "refund"
    UNBLOCK = "unblock"


    @property
    def description(self) -> str:
        descriptions = {
            self.NEW: "Платеж создан и ссылка на платежную форму сформирована. Клиент не ввел данные карты",
            self.SECURE_3D: "Платеж на проверке 3DS",
            self.AUTH: "Платеж авторизован. Средства заблокированы. Необходимо подтвердить платеж",
            self.SUCCESS: "Платеж обработан успешно",
            self.ERROR: "Платеж в состоянии ошибка",
            self.RETURN: "Платеж возвращен полностью",
            self.REFUND: "Платеж возвращен частично",
            self.UNBLOCK: "Платеж разблокирован",
        }
        return descriptions.get(self, "Неизвестный статус платежа")
    

class PaymentErrorCode(IntEnum):    
    NO_ERROR = 0
    DUPLICATE_TRANSACTION = 5001
    INVALID_CARD_NUMBER = 5002
    INVALID_CARD_EXPIRY = 5003
    INVALID_AMOUNT = 5004
    INVALID_CURRENCY = 5005
    INVALID_CVC = 5006
    INSUFFICIENT_FUNDS = 5007
    AMOUNT_LIMIT_EXCEEDED = 5008
    INVALID_3DS_CODE = 5009
    BLOCKED_BY_ANTIFRAUD = 5100
    PAYMENT_SYSTEM_ERROR = 5998
    ACQUIRER_BANK_ERROR = 5999
    
    @property
    def description(self) -> str:
        descriptions = {
            self.NO_ERROR: "Нет ошибки",
            self.DUPLICATE_TRANSACTION: "Дублированная транзакция в банке-эквайере",
            self.INVALID_CARD_NUMBER: "Ошибка в номере карты",
            self.INVALID_CARD_EXPIRY: "Ошибка в сроке действия карты",
            self.INVALID_AMOUNT: "Ошибка в сумме",
            self.INVALID_CURRENCY: "Ошибка в валюте",
            self.INVALID_CVC: "Ошибка в CVC",
            self.INSUFFICIENT_FUNDS: "Недостаточно средств на карте",
            self.AMOUNT_LIMIT_EXCEEDED: "Сумма превышает допустимый лимит",
            self.INVALID_3DS_CODE: "Неверно введен код 3DS",
            self.BLOCKED_BY_ANTIFRAUD: "Заблокировано антифродом",
            self.PAYMENT_SYSTEM_ERROR: "Ошибка в платежной системе",
            self.ACQUIRER_BANK_ERROR: "Ошибка в банке-эквайере",
        }
        return descriptions[self]