from app.services.validators import is_valid_ipv4, is_valid_ipv6, is_valid_prefix, is_valid_community, is_valid_aspath_regex, get_ip_version

class TestValidators:
    def test_valid_ipv4(self):
        assert is_valid_ipv4("8.8.8.8") is True
        assert is_valid_ipv4("0.0.0.0") is True

    def test_invalid_ipv4(self):
        assert is_valid_ipv4("999.999.999.999") is False
        assert is_valid_ipv4("not-an-ip") is False

    def test_valid_ipv6(self):
        assert is_valid_ipv6("2001:db8::1") is True
        assert is_valid_ipv6("::1") is True

    def test_invalid_ipv6(self):
        assert is_valid_ipv6("not-ipv6") is False
        assert is_valid_ipv6("8.8.8.8") is False

    def test_valid_prefix(self):
        assert is_valid_prefix("203.0.113.0/24") is True
        assert is_valid_prefix("2001:db8::/32") is True

    def test_valid_community(self):
        assert is_valid_community("65000:100") is True
        assert is_valid_community("65000:100:200") is True

    def test_invalid_community(self):
        assert is_valid_community("invalid") is False
        assert is_valid_community("65000") is False

    def test_valid_aspath(self):
        assert is_valid_aspath_regex("^65000_") is True

    def test_invalid_aspath(self):
        assert is_valid_aspath_regex("echo hello") is False

    def test_ip_version(self):
        assert get_ip_version("8.8.8.8") == 4
        assert get_ip_version("2001:db8::1") == 6
        assert get_ip_version("203.0.113.0/24") == 4
