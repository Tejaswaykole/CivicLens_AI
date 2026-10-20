"""Alembic environment. The database URL always comes from application settings."""

import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

BACKEND_ROOT = Path(__file__).resolve().parents[1]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.core.config import clear_settings_cache, get_settings  # noqa: E402
from app.models import Base  # noqa: E402

try:
    config = context.config
except AttributeError:
    config = None

if config is not None and getattr(config, "config_file_name", None) is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def database_url() -> str:
    clear_settings_cache()
    settings = get_settings()
    url = settings.direct_url or settings.database_url
    if not url:
        raise RuntimeError(
            "Neither DIRECT_URL nor DATABASE_URL is set. Alembic will not fall back to a hardcoded database URL."
        )
    # ConfigParser treats % as interpolation.
    return url.replace("%", "%%")


def run_migrations_offline() -> None:
    context.configure(
        url=database_url(),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    configuration = config.get_section(config.config_ini_section) or {}
    configuration["sqlalchemy.url"] = database_url()
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


def get_database_url() -> str:
    """Public helper matching database_url."""
    return database_url()


if config is not None and getattr(config, "config_file_name", None) is not None:
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        run_migrations_online()
