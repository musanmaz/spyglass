import pytest
from pydantic import ValidationError
from app.api.v1.schemas.query import QueryRequest

class TestInputSanitization:
    def test_valid_bgp_route_query(self):
        q = QueryRequest(query_type="bgp_route", target="203.0.113.0/24", device_ids=["test-router"])
        assert q.query_type == "bgp_route"
        assert q.target == "203.0.113.0/24"

    def test_valid_ping_query(self):
        q = QueryRequest(query_type="ping", target="8.8.8.8", device_ids=["test-router"])
        assert q.target == "8.8.8.8"

    def test_invalid_query_type(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="show_run", target="8.8.8.8", device_ids=["test-router"])

    def test_shell_injection_semicolon(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="ping", target="8.8.8.8; cat /etc/passwd", device_ids=["test-router"])

    def test_shell_injection_pipe(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="ping", target="8.8.8.8 | rm -rf /", device_ids=["test-router"])

    def test_shell_injection_backtick(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="ping", target="`whoami`", device_ids=["test-router"])

    def test_shell_injection_dollar(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="ping", target="$(cat /etc/passwd)", device_ids=["test-router"])

    def test_newline_injection(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="ping", target="8.8.8.8\nshow run", device_ids=["test-router"])

    def test_config_leak_show_run(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="bgp_route", target="show running-config", device_ids=["test-router"])

    def test_config_mode_attempt(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="bgp_route", target="configure terminal", device_ids=["test-router"])

    def test_dangerous_commands_delete(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="bgp_route", target="delete flash:", device_ids=["test-router"])

    def test_dangerous_commands_reload(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="bgp_route", target="reload", device_ids=["test-router"])

    def test_path_traversal(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="bgp_route", target="../../../etc/passwd", device_ids=["test-router"])

    def test_loopback_address(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="ping", target="127.0.0.1", device_ids=["test-router"])

    def test_link_local_address(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="ping", target="169.254.1.1", device_ids=["test-router"])

    def test_empty_target(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="ping", target="", device_ids=["test-router"])

    def test_too_many_devices(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="ping", target="8.8.8.8", device_ids=["d1", "d2", "d3", "d4", "d5", "d6"])

    def test_no_devices(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="ping", target="8.8.8.8", device_ids=[])

    def test_invalid_device_id_format(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="ping", target="8.8.8.8", device_ids=["INVALID_ID!"])

    def test_valid_community(self):
        q = QueryRequest(query_type="bgp_community", target="65000:100", device_ids=["test-router"])
        assert q.target == "65000:100"

    def test_invalid_community(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="bgp_community", target="not-a-community", device_ids=["test-router"])

    def test_valid_aspath(self):
        q = QueryRequest(query_type="bgp_aspath", target="^65000_", device_ids=["test-router"])
        assert q.target == "^65000_"

    def test_too_wide_ipv4_prefix(self):
        with pytest.raises(ValidationError):
            QueryRequest(query_type="bgp_route", target="0.0.0.0/4", device_ids=["test-router"])

    def test_valid_ipv6(self):
        q = QueryRequest(query_type="bgp_route", target="2001:db8::/32", device_ids=["test-router"])
        assert q.target == "2001:db8::/32"
