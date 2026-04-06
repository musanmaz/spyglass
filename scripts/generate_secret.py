#!/usr/bin/env python3
"""Generate a cryptographically secure secret key."""

import secrets
import sys


def main() -> None:
    key = secrets.token_urlsafe(48)
    if "--env" in sys.argv:
        print(f"SECRET_KEY={key}")
    else:
        print(key)


if __name__ == "__main__":
    main()
