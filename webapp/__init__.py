from flask import Flask

from webapp.config import get_config_class
from webapp import handlers
from webapp.utils import fail_jsonify, JSONEncoder


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config_class())

    init_errorhandler(app)
    app.json_encoder = JSONEncoder
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


def init_errorhandler(app):

    @app.errorhandler(400)
    @app.errorhandler(401)
    @app.errorhandler(403)
    @app.errorhandler(404)
    def handle_error(e):
        # fake bytes, since almost same bytes size
        return fail_jsonify(data=e.description, reason=str(e)), e.code

    @app.errorhandler(500)
    def handle_server_error(e):
        # fake bytes, since almost same bytes size
        return fail_jsonify(data=None, reason='500 Internal server error'), 500
