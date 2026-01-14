from enum import Enum


class Role(Enum):
    ADMIN = "admin"
    USER = "user"
    PARENT = "parent"
    CHILD = "child"
    PARTNER = "partner"