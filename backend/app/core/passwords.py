"""Argon2id password hashing. Plaintext passwords are never stored or logged."""

from pwdlib import PasswordHash

_hasher = PasswordHash.recommended()
_dummy_hash: str | None = None

MIN_PASSWORD_LENGTH = 12
MAX_PASSWORD_LENGTH = 128


def password_is_acceptable(password: str) -> bool:
    if not isinstance(password, str):
        return False
    if password != password.strip():
        return False
    return MIN_PASSWORD_LENGTH <= len(password) <= MAX_PASSWORD_LENGTH


def hash_password(password: str) -> str:
    if not password_is_acceptable(password):
        raise ValueError("Password does not meet the length requirements.")
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    """Return whether the password matches. A missing hash still runs a hash check."""
    candidate = password if isinstance(password, str) else ""
    stored = password_hash or _dummy()
    try:
        matched = _hasher.verify(candidate, stored)
    except Exception:
        return False
    return bool(matched) and password_hash is not None


def _dummy() -> str:
    global _dummy_hash
    if _dummy_hash is None:
        _dummy_hash = _hasher.hash("not-a-user-password")
    return _dummy_hash
