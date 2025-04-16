from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import os
import sys
from dotenv import load_dotenv

# Add the project root directory to the Python path
# Adjust this path if your project structure is different
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# Load environment variables from .env file in the project root
load_dotenv(os.path.join(project_root, '.env'))

# this is the Alembic Config object
config = context.config

# Set the database URL directly from the environment variable
db_url = os.getenv("DATABASE_URL")
if not db_url:
    raise ValueError("DATABASE_URL environment variable not set")
config.set_main_option("sqlalchemy.url", db_url)

# Interpret the config file for Python logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Import your models' Base metadata
# Make sure the path to your models is correct
from backend.app.models.base import Base
# You might need to explicitly import each model if they aren't automatically loaded by importing Base
# For example:
from backend.app.models.user import User
from backend.app.models.message import Message
from backend.app.models.user_note import UserNote
from backend.app.models.user_skill import UserSkill
from backend.app.models.user_profile import UserProfile
from backend.app.models.suggested_peers import SuggestedPeers # Fixed the class name here
from backend.app.models.saved_recommendation import SavedRecommendation

# Add your model's MetaData object here for 'autogenerate' support
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
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
    """Run migrations in 'online' mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
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