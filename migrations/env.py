from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool

from app.core.config import get_settings
from app.core.db import Base, normalize_database_url
from app.modules.alerts import models as alerts_models  # noqa: F401  (registra sus tablas)
from app.modules.auth import models as auth_models  # noqa: F401  (registra sus tablas en Base)
from app.modules.billing import models as billing_models  # noqa: F401  (registra sus tablas)
from app.modules.farms import models as farms_models  # noqa: F401  (registra sus tablas en Base)
from app.modules.marketplace import models as marketplace_models  # noqa: F401  (registra tablas)
from app.modules.privacy import models as privacy_models  # noqa: F401  (registra sus tablas)
from app.modules.rotation import models as rotation_models  # noqa: F401  (registra sus tablas)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# La URL viene de DATABASE_URL (ver app.core.config), nunca de alembic.ini.
config.set_main_option("sqlalchemy.url", normalize_database_url(get_settings().database_url))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
