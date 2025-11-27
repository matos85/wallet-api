import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Добавляем корень проекта в sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Импортируем Base после добавления пути
from app.models import Base  # noqa: E402

config = context.config

# Убираем ошибку KeyError: 'formatters'
# fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Берем URL из переменной окружения и заменяем asyncpg → psycopg2 только для Alembic
db_url = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://user:password@db:5432/dbname"
)
# Alembic не умеет работать с asyncpg → используем синхронный драйвер
config.set_main_option("sqlalchemy.url", db_url.replace("asyncpg", "psycopg2"))


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
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