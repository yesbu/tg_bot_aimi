from enum import Enum


class Role(Enum):
    ADMIN = "ADMIN"
    USER = "USER"
    PARENT = "PARENT"
    CHILD = "CHILD"
    PARTNER = "PARTNER"