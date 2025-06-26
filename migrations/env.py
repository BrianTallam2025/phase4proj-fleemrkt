import logging
from logging.config import fileConfig

from flask import current_app
from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Set up logger before any logging calls
logger = logging.getLogger('alembic.env')

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)
    logger.info('Configured logging from %s', config.config_file_name)

def get_engine():
    try:
        # this works with Flask-SQLAlchemy<3 and Alchemical
        return current_app.extensions['migrate'].db.get_engine()
    except (TypeError, AttributeError) as e:
        logger.debug('Fallback to Flask-SQLAlchemy>=3 style engine access')
        # this works with Flask-SQLAlchemy>=3
        return current_app.extensions['migrate'].db.engine

def get_engine_url():
    try:
        url = get_engine().url.render_as_string(hide_password=False).replace('%', '%%')
        logger.debug('Engine URL: %s', url)
        return url
    except AttributeError as e:
        logger.warning('Could not render engine URL with password hiding')
        return str(get_engine().url).replace('%', '%%')

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
config.set_main_option('sqlalchemy.url', get_engine_url())
target_db = current_app.extensions['migrate'].db

def get_metadata():
    if hasattr(target_db, 'metadatas'):
        logger.debug('Using metadatas attribute for database metadata')
        return target_db.metadatas[None]
    logger.debug('Using direct metadata attribute')
    return target_db.metadata

def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    logger.info('Running migrations in OFFLINE mode')
    
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=get_metadata(),
        literal_binds=True,
        compare_type=True,
        compare_server_default=True
    )

    with context.begin_transaction():
        context.run_migrations()
        logger.info('Offline migrations complete')

def run_migrations_online():
    """Run migrations in 'online' mode."""
    logger.info('Running migrations in ONLINE mode')

    def process_revision_directives(context, revision, directives):
        if getattr(config.cmd_opts, 'autogenerate', False):
            script = directives[0]
            if script.upgrade_ops.is_empty():
                directives[:] = []
                logger.info('No schema changes detected - skipping migration')

    conf_args = current_app.extensions['migrate'].configure_args
    if conf_args.get("process_revision_directives") is None:
        conf_args["process_revision_directives"] = process_revision_directives

    connectable = get_engine()
    logger.debug('Obtained database engine: %s', connectable)

    with connectable.connect() as connection:
        logger.debug('Established database connection')
        context.configure(
            connection=connection,
            target_metadata=get_metadata(),
            **conf_args
        )

        with context.begin_transaction():
            logger.info('Starting migration transaction')
            context.run_migrations()
            logger.info('Migrations completed successfully')

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()