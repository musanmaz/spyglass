import pytest
from unittest.mock import MagicMock
from app.api.middleware.trusted_proxy import get_client_ip, _is_trusted_proxy

class TestTrustedProxy:
    def test_direct_connection(self):
        request = MagicMock()
        request.headers = {}
        request.client.host = "85.105.1.1"
        assert get_client_ip(request) == "85.105.1.1"

    def test_x_real_ip_header(self):
        request = MagicMock()
        request.headers = {"x-real-ip": "85.105.1.1"}
        request.client.host = "10.0.0.1"
        assert get_client_ip(request) == "85.105.1.1"

    def test_xff_with_trusted_proxy(self):
        request = MagicMock()
        request.headers = {"x-forwarded-for": "85.105.1.1, 10.0.1.50"}
        request.client.host = "10.0.1.1"
        assert get_client_ip(request) == "85.105.1.1"

    def test_xff_spoofing_blocked(self):
        """Attacker adds fake IP to XFF — should still resolve to real client."""
        request = MagicMock()
        request.headers = {"x-forwarded-for": "1.2.3.4, 85.105.1.1, 10.0.1.50"}
        request.client.host = "10.0.1.1"
        ip = get_client_ip(request)
        assert ip == "85.105.1.1"

    def test_xff_all_trusted(self):
        request = MagicMock()
        request.headers = {"x-forwarded-for": "10.0.0.5, 10.0.1.50"}
        request.client.host = "10.0.1.1"
        ip = get_client_ip(request)
        assert ip == "10.0.0.5"

    def test_private_ip_is_trusted(self):
        assert _is_trusted_proxy("10.0.0.1") is True
        assert _is_trusted_proxy("172.16.0.1") is True
        assert _is_trusted_proxy("192.168.1.1") is True
        assert _is_trusted_proxy("127.0.0.1") is True

    def test_public_ip_is_not_trusted(self):
        assert _is_trusted_proxy("85.105.1.1") is False
        assert _is_trusted_proxy("8.8.8.8") is False

    def test_invalid_ip_not_trusted(self):
        assert _is_trusted_proxy("not-an-ip") is False
        assert _is_trusted_proxy("") is False

    def test_no_client(self):
        request = MagicMock()
        request.headers = {}
        request.client = None
        assert get_client_ip(request) == "0.0.0.0"

    def test_invalid_x_real_ip_falls_through(self):
        request = MagicMock()
        request.headers = {"x-real-ip": "not-valid"}
        request.client.host = "85.105.1.1"
        assert get_client_ip(request) == "85.105.1.1"
