import importlib
from logging.config import fileConfig


from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

from db import SQL_DB_URL, Base

# --- AUTOMATIC MODEL DISCOVERY ---
import importlib
from pathlib import Path

# --- MODERN AUTO-DISCOVERY ---
def discover_models():
    # 1. Find the absolute path of your "modules" folder
    # Assuming env.py is in root/migrations/
    root_dir = Path(__file__).resolve().parent.parent
    modules_dir = root_dir / "modules"

    # 2. Search for every "models.py" file
    for path in modules_dir.rglob("models.py"):
        # 3. Convert system path to Python module path (e.g., modules.users.models)
        module_path = path.relative_to(root_dir).with_suffix("")
        module_name = ".".join(module_path.parts)
        
        print(f"DEBUG: Loading {module_name}") # This confirms it works
        importlib.import_module(module_name)

discover_models()
# -----------------------------
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
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = SQL_DB_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """

    section = config.get_section(config.config_ini_section, {})
    section["sqlalchemy.url"] = SQL_DB_URL
    
    connectable = engine_from_config(
        section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
