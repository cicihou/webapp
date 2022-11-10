import logging
import statsd

from flask import Flask, request

from webapp.config import get_config_class, CONF
from webapp import handlers
from webapp.utils import fail_jsonify, JSONEncoder, now


def create_app():
    app = Flask(__name__)
    app.config.from_object(get_config_class())

    init_errorhandler(app)
    app.json_encoder = JSONEncoder
    configure_log(app)
    init_log(app)
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

    logger = logging.getLogger('webapp')
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(app.config.get('LOG_FORMAT')))
    logger.addHandler(handler)
    file_handler = logging.FileHandler(app.config.get('LOG_FILE_PATH'))
    logger.addHandler(file_handler)
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


def access_log(code):
    logger = logging.getLogger(__name__)
    try:
        log = dict(
            remote_addr=request.headers.get('X-Real-IP') or request.remote_addr,
            endpoint=request.endpoint,
            time=now().strftime('%Y-%m-%d %H:%M:%S'),
            method=request.method,
            code=code,
            path=request.full_path
        )
        logger.info(log)
    except Exception:
        pass


def count_endpoint():
    c = statsd.StatsClient(CONF.STATSD_HOST, CONF.STATSD_PORT, prefix=CONF.STATSD_PREFIX)
    c.incr(request.endpoint)


def init_log(app):
    @app.after_request
    def after_request(response):
        if request.endpoint:
            access_log(response.status_code)
            count_endpoint()
        return response
