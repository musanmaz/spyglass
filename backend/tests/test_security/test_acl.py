import pytest
from app.services.acl_checker import AclChecker

class TestAclChecker:
    @pytest.fixture
    def checker(self):
        return AclChecker("config/acl.yaml")

    def test_public_ip_allowed(self, checker):
        assert checker.check_target("8.8.8.8") is None

    def test_public_prefix_allowed(self, checker):
        assert checker.check_target("203.0.113.0/24") is None

    def test_private_10_denied(self, checker):
        result = checker.check_target("10.0.0.1")
        assert result is not None
        assert "sorgulanamaz" in result

    def test_private_172_denied(self, checker):
        result = checker.check_target("172.16.0.1")
        assert result is not None

    def test_private_192_denied(self, checker):
        result = checker.check_target("192.168.1.1")
        assert result is not None

    def test_loopback_denied(self, checker):
        result = checker.check_target("127.0.0.1")
        assert result is not None

    def test_link_local_denied(self, checker):
        result = checker.check_target("169.254.1.1")
        assert result is not None

    def test_multicast_denied(self, checker):
        result = checker.check_target("224.0.0.1")
        assert result is not None

    def test_too_wide_prefix(self, checker):
        result = checker.check_target("0.0.0.0/4")
        assert result is not None
        assert "Prefix" in result

    def test_valid_prefix_length(self, checker):
        assert checker.check_target("8.8.8.0/24") is None
