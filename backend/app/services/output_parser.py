import re

class OutputParser:
    @staticmethod
    def sanitize(output: str) -> str:
        """Remove sensitive information from router output."""
        output = re.sub(r'(?i)(password|secret|community)\s*[:=]\s*\S+', r'\1: ****', output)
        output = re.sub(r'(?i)snmp-server community \S+', 'snmp-server community ****', output)
        output = re.sub(r'(?i)(ssh-rsa|ssh-ed25519)\s+\S+', r'\1 [REDACTED]', output)
        output = re.sub(r'(?i)(key|certificate)\s+\S{20,}', r'\1 [REDACTED]', output)
        return output.strip()

    @staticmethod
    def truncate(output: str, max_length: int = 64000) -> str:
        if len(output) > max_length:
            return output[:max_length] + "\n\n... [Output truncated] ..."
        return output
