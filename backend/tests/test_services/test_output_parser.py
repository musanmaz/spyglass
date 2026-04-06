from app.services.output_parser import OutputParser

class TestOutputParser:
    def test_sanitize_password(self):
        output = "password: mysecret123"
        result = OutputParser.sanitize(output)
        assert "mysecret123" not in result
        assert "****" in result

    def test_sanitize_snmp_community(self):
        output = "snmp-server community public123"
        result = OutputParser.sanitize(output)
        assert "public123" not in result

    def test_sanitize_ssh_key(self):
        output = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABgQC7..."
        result = OutputParser.sanitize(output)
        assert "[REDACTED]" in result

    def test_truncate_long_output(self):
        output = "x" * 100000
        result = OutputParser.truncate(output, max_length=1000)
        assert len(result) < 100000
        assert "[Output truncated]" in result

    def test_normal_output_not_truncated(self):
        output = "normal output"
        result = OutputParser.truncate(output)
        assert result == "normal output"
