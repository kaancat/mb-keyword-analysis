"""
Central credentials loader for mondaybrew services.
Loads from ~/.mondaybrew/.env first, then falls back to local .env
"""

import os
from pathlib import Path


def load_credentials():
    """
    Load credentials from central location (~/.mondaybrew/.env) first,
    then fall back to local .env if central doesn't exist.
    """
    from dotenv import load_dotenv

    # Primary: Central credentials in home directory
    central_env = Path.home() / ".mondaybrew" / ".env"

    # Secondary: Local .env in current working directory
    local_env = Path.cwd() / ".env"

    # Load central first (if exists)
    if central_env.exists():
        load_dotenv(central_env)
        return str(central_env)

    # Fall back to local
    if local_env.exists():
        load_dotenv(local_env)
        return str(local_env)

    # No credentials found
    return None


def ensure_credentials():
    """
    Ensure credentials are loaded. Raises error if not found.
    """
    source = load_credentials()
    if source is None:
        raise EnvironmentError(
            "No credentials found. Please create ~/.mondaybrew/.env with your API credentials.\n"
            "See .env.example for required variables."
        )
    return source
