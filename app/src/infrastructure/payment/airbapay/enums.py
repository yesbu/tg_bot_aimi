from enum import Enum


class AirbaPaymentStatus(str, Enum):
    NEW = "new"
    AUTH = "auth"
    SUCCESS = "success"
    ERROR = "error"
    CANCELLED = "cancelled"


class AirbaLanguage(str, Enum):
    RU = "ru"
    EN = "en"
    KZ = "kz"


class AirbaAutoCharge(int, Enum):
    TWO_STAGE = 0
    ONE_STAGE = 1
