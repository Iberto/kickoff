from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context
from src.config import settings
from src.models import Base

# List of my schemas
AVAILABLE_SCHEMAS = (None, "audit", "public")

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


# utility to consider only our schemas
def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table":
        return object.schema in AVAILABLE_SCHEMAS
    if type_ == "index" and reflected and compare_to is None:
        # Index exists in DB but not in models — likely created by TimescaleDB
        return False
    return True


# shared config for online and offline migrations
_configure_opts: dict = {
    "target_metadata": target_metadata,
    "include_schemas": True,
    "include_object": include_object,
}


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    # if we use alembic.ini
    # url = config.get_main_option("sqlalchemy.url")
    url = settings.database_url_sync
    context.configure(
        url=url,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **_configure_opts,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # connectable = engine_from_config(
    #     config.get_section(config.config_ini_section, {}),
    #     prefix="sqlalchemy.",
    #     poolclass=pool.NullPool,
    # )
    connectable = create_engine(
        url=settings.database_url_sync,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            **_configure_opts,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
