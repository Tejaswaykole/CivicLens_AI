"""Refuse to serve when the listen address and JWT settings disagree.

API_HOST is the address the operator declares. Uvicorn has its own --host.
Those two values used to be checked separately, so API_HOST=127.0.0.1 could
start without a JWT secret while Uvicorn listened on 0.0.0.0. Startup now
reads the Uvicorn Config that is loading or serving this process and stops
before the application accepts connections when the two do not describe the
same exposure.
"""

import inspect
from dataclasses import dataclass

from app.core.config import Settings, get_settings
from app.core.tokens import host_is_loopback, secret_is_acceptable

_SECRET_REQUIRED = (
    "Set a JWT_SECRET of at least 32 characters with 8 or more distinct characters "
    "when APP_ENV=production or the server binds beyond loopback. "
    "The application does not generate a secret."
)


class BindSecurityError(RuntimeError):
    """Startup must stop. The listen address is not allowed by the current settings."""


@dataclass(frozen=True)
class ServerBind:
    host: str | None
    inherited_fd: int | None
    unix_socket: str | None


def discover_server_bind() -> ServerBind | None:
    """Return Uvicorn's bind target when called from Uvicorn. Otherwise return None."""
    frame = inspect.currentframe()
    try:
        while frame is not None:
            config = _uvicorn_config_from_frame(frame)
            if config is not None:
                return ServerBind(
                    host=getattr(config, "host", None),
                    inherited_fd=getattr(config, "fd", None),
                    unix_socket=getattr(config, "uds", None),
                )
            frame = frame.f_back
    finally:
        del frame
    return None


def enforce_server_bind(settings: Settings | None = None) -> None:
    """Stop startup when the live bind host is public or does not match API_HOST."""
    discovered = discover_server_bind()
    if discovered is None:
        return
    current = settings or get_settings()
    if discovered.inherited_fd is not None:
        raise BindSecurityError(
            "The server was given a pre-bound socket, so its listen address cannot be "
            "checked against API_HOST. Start Uvicorn with --host set to the same value "
            "as API_HOST."
        )
    if discovered.unix_socket is not None:
        raise BindSecurityError(
            "The server is bound to a Unix socket. API_HOST cannot describe that listener. "
            "Start Uvicorn with --host set to the same value as API_HOST."
        )
    actual = discovered.host
    if not isinstance(actual, str) or not actual.strip():
        raise BindSecurityError("The server bind host could not be read. Refusing to start.")
    declared = current.api_host
    if not _same_exposure(declared, actual):
        raise BindSecurityError(
            f"API_HOST is {declared}, but the server is binding to {actual.strip().lower()}. "
            "Set --host to the same address as API_HOST. "
            "Loopback names such as 127.0.0.1, localhost, and ::1 match each other. "
            + _SECRET_REQUIRED
        )
    exposed = current.app_env == "production" or not host_is_loopback(actual)
    if exposed and not secret_is_acceptable(current.jwt_secret):
        raise BindSecurityError(_SECRET_REQUIRED)


def _same_exposure(declared: str, actual: str) -> bool:
    if host_is_loopback(declared) and host_is_loopback(actual):
        return True
    return declared.strip().lower() == actual.strip().lower()


def _uvicorn_config_from_frame(frame: object) -> object | None:
    locals_ = getattr(frame, "f_locals", {})
    candidates: list[object] = []
    owner = locals_.get("self")
    if owner is not None:
        candidates.append(owner)
        nested = getattr(owner, "config", None)
        if nested is not None:
            candidates.append(nested)
    named = locals_.get("config")
    if named is not None:
        candidates.append(named)
    for candidate in candidates:
        kind = type(candidate)
        if kind.__name__ == "Config" and kind.__module__.startswith("uvicorn."):
            return candidate
    return None
