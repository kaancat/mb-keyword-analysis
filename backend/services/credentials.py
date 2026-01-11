"""
Central credentials loader for mondaybrew services.
Loads from ~/.mondaybrew/.env - works from any directory.
"""

import os
from pathlib import Path


def load_credentials():
    """
    Load credentials from central location (~/.mondaybrew/.env).
    Returns the path if loaded, None if not found.
    """
    from dotenv import load_dotenv

    # Central credentials in home directory
    central_env = Path.home() / ".mondaybrew" / ".env"

    if central_env.exists():
        load_dotenv(central_env)
        return str(central_env)

    return None


def ensure_credentials():
    """
    Ensure credentials are loaded. Raises error if not found.
    This should fail LOUDLY so Claude knows the API won't work.
    """
    source = load_credentials()
    if source is None:
        raise EnvironmentError(
            "\n" + "=" * 60 + "\n"
            "CREDENTIALS NOT FOUND\n"
            "=" * 60 + "\n"
            "Please create ~/.mondaybrew/.env with your API credentials.\n"
            "See .env.example for required variables.\n"
            "=" * 60
        )
    return source
