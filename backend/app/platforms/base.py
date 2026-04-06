from abc import ABC, abstractmethod
from typing import Set

class PlatformBase(ABC):
    @property
    @abstractmethod
    def name(self) -> str: ...

    @property
    @abstractmethod
    def platform_key(self) -> str: ...

    @property
    @abstractmethod
    def netmiko_device_type(self) -> str: ...

    @property
    @abstractmethod
    def supported_queries(self) -> Set[str]: ...
