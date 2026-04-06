from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from app.models.device import Device
from app.models.query_log import QueryLog
from app.models.acl import AclRule

__all__ = ["Base", "Device", "QueryLog", "AclRule"]
