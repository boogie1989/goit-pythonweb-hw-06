"""
Alembic environment configuration for database migrations.

This script sets up the Alembic migration environment, including the database connection
and metadata for running migrations in both online and offline modes.
"""

# Import necessary modules for Alembic configuration
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context  # pylint: disable=no-name-in-module

# Import the Base metadata from your models
from models import Base

# Get the Alembic Config object, which provides access to the values within the .ini file
config = context.config  # pylint: disable=no-member

# Set up Python logging from the config file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Set the target metadata for autogenerating migrations
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """
    Run migrations in 'offline' mode.

    This configures the context with just a URL and not an Engine, though an Engine is
    acceptable here as well. By skipping the Engine creation, we don't even need a DBAPI
    to be available. Calls to context.execute() here emit the given string to the script output.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(  # pylint: disable=no-member
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():  # pylint: disable=no-member
        context.run_migrations()  # pylint: disable=no-member

def run_migrations_online() -> None:
    """
    Run migrations in 'online' mode.

    In this scenario, we need to create an Engine and associate a connection with the context.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(  # pylint: disable=no-member
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():  # pylint: disable=no-member
            context.run_migrations()  # pylint: disable=no-member

# Run migrations based on the mode (offline or online)
if context.is_offline_mode():  # pylint: disable=no-member
    run_migrations_offline()
else:
    run_migrations_online()
