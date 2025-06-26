# backend/migrations/env.py
# This file is part of the Alembic migration environment for Flask-Migrate.
# It defines how Alembic interacts with your Flask application and its database
# to perform schema migrations.

import logging
from logging.config import fileConfig

from flask import current_app
from alembic import context

# This is the Alembic Config object, which provides
# access to the values within the .ini file (e.g., alembic.ini) in use.
config = context.config

# Set up logger before any logging calls for Alembic's own output.
logger = logging.getLogger('alembic.env')

# Interpret the config file for Python logging.
# This line sets up loggers based on the [logger_alembic] and other
# configurations in alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
    logger.info('Configured logging from %s', config.config_file_name)

def get_engine():
    """
    Retrieves the database engine from the Flask application's Flask-Migrate extension.
    This handles different versions of Flask-SQLAlchemy.
    """
    try:
        # This works with Flask-SQLAlchemy < 3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError) as e:
        logger.debug('Fallback to Flask-SQLAlchemy>=3 style engine access: %s', e)
        # This works with Flask-SQLAlchemy >= 3
        return current_app.extensions['migrate'].db.engine

def get_engine_url():
    """
    Renders the database connection URL for Alembic.
    Includes password (if present) for migration operations, but attempts to hide it for logs.
    """
    try:
        # Render the URL, replacing '%' with '%%' for string formatting safety.
        # hide_password=False is often used here so Alembic can fully connect,
        # but in logs it might still be masked depending on the logger's configuration.
        url = get_engine().url.render_as_string(hide_password=False).replace('%', '%%')
        logger.debug('Engine URL: %s', url)
        return url
    except AttributeError as e:
        logger.warning('Could not render engine URL with password hiding: %s', e)
        # Fallback for older SQLAlchemy versions or unusual setups.
        return str(get_engine().url).replace('%', '%%')

# Add your model's MetaData object here for 'autogenerate' support.
# Flask-Migrate automatically gets this from your db.Model setup via the 'db' instance.
# We ensure that alembic's sqlalchemy.url config option is set to the correct database.
config.set_main_option('sqlalchemy.url', get_engine_url())

# Target database instance from Flask-Migrate extension.
# This is how Alembic gets access to your SQLAlchemy models' metadata.
target_db = current_app.extensions['migrate'].db

def get_metadata():
    """
    Retrieves the MetaData object associated with the SQLAlchemy declarative base.
    This is used by Alembic to compare the current database schema against your models.
    """
    if hasattr(target_db, 'metadatas'):
        # For setups with multiple metadata objects (less common).
        logger.debug('Using metadatas attribute for database metadata.')
        return target_db.metadatas[None] # Assuming default metadata
    logger.debug('Using direct metadata attribute.')
    return target_db.metadata

def run_migrations_offline():
    """
    Run migrations in 'offline' mode.
    This mode generates SQL scripts without connecting to the database.
    """
    logger.info('Running migrations in OFFLINE mode.')
    
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True, # Render all parameters as literals within the DDL.
        compare_type=True, # Enable type comparison for autogenerate.
        compare_server_default=True # Enable server default comparison for autogenerate.
    )

    with context.begin_transaction():
        context.run_migrations()
        logger.info('Offline migrations complete.')

def run_migrations_online():
    """
    Run migrations in 'online' mode.
    This mode connects to the database and applies migrations directly.
    """
    logger.info('Running migrations in ONLINE mode.')

    def process_revision_directives(context, revision, directives):
        """
        A callback function used by autogenerate to inspect the generated directives.
        If no schema changes are detected, it prevents an empty migration script from being created.
        """
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = [] # Clear the directives list
                logger.info('No schema changes detected - skipping migration.')

    # Get additional configuration arguments from Flask-Migrate.
    conf_args = current_app.extensions['migrate'].configure_args
    # If a process_revision_directives hook isn't already set, use ours.
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()
    logger.debug('Obtained database engine: %s', connectable)

    with connectable.connect() as connection:
        logger.debug('Established database connection.')
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args # Pass additional configuration arguments
        )

        with context.begin_transaction():
            logger.info('Starting migration transaction.')
            context.run_migrations()
            logger.info('Migrations completed successfully.')

# Determine whether to run in offline or online mode based on Alembic's context.
if context.is_offline_mode():
    run_migrations_offline()
else:
    # Ensure the Flask application context is active for online migrations.
    # This is critical for Flask-Migrate to access app.config and extensions.
    with current_app.app_context():
        run_migrations_online()
