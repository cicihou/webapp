from flask import Flask

from webapp.config import get_config_class
from webapp import handlers


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config_class())

    configure_log(app)
    register_extensions(app)

    from webapp import models  # noqa
    return app


def register_extensions(app):
    from webapp.extensions import db, migrate

    db.init_app(app)
    migrate.init_app(app=app, db=db)
    handlers.init_app(app)


def configure_log(app):
    import logging

    if not app.config['DEBUG']:
        app.logger.addHandler(logging.StreamHandler())
        app.logger.setLevel(logging.INFO)

    logger = logging.getLogger('thiqa')
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(app.config.get('LOG_FORMAT')))
    logger.addHandler(handler)
    logger.setLevel(app.config.get('LOG_LEVEL'))
