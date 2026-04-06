class LookingGlassError(Exception):
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)


class DeviceConnectionError(LookingGlassError):
    def __init__(self, device_id: str, message: str = "Failed to connect to device"):
        super().__init__(f"{message}: {device_id}", 503)
        self.device_id = device_id


class QueryTimeoutError(LookingGlassError):
    def __init__(self, device_id: str):
        super().__init__(f"Query timed out: {device_id}", 408)
        self.device_id = device_id


class TargetDeniedError(LookingGlassError):
    def __init__(self, target: str):
        super().__init__(f"Query not allowed for this target: {target}", 403)
        self.target = target


class SecurityError(LookingGlassError):
    def __init__(self, message: str = "Security violation detected"):
        super().__init__(message, 403)


class DeviceNotFoundError(LookingGlassError):
    def __init__(self, device_id: str):
        super().__init__(f"Device not found: {device_id}", 404)
        self.device_id = device_id
