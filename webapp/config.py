import logging
import os


class Config(object):
    # noinspection PyPackageRequirements
    DEBUG = False

    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    LOG_LEVEL = logging.INFO

    # Flask-SQLAlchemy settings
    DB_USERNAME = 'root'
    DB_PASSWORD = 'mysql1234'
    DB_HOST = 'localhost'
    DB = 'webapp'
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}/{DB}?charset=utf8mb4'
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BCRYPT_SALT = b'$2b$12$Hw4dlmptnnOJ4RdCyimiVO'
    S3_BUCKET = os.environ.get('S3_BUCKET', '')

    LOG_FILE_PATH = '/var/log/csye6225.log'

    STATSD_HOST = 'localhost'
    STATSD_PORT = 8125
    STATSD_PREFIX = 'webapp'


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    LOG_LEVEL = logging.INFO
    SQLALCHEMY_ECHO = False
    DB_USERNAME = 'csye6225'
    DB_PASSWORD = os.environ.get('DB_PASSWORD'.upper(), 'mysql1234')
    DB_HOST = os.environ.get('DB_HOST'.upper(), 'localhost')
    DB = 'csye6225'
    SQLALCHEMY_DATABASE_URI = f'mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:3306/{DB}?charset=utf8mb4'


def get_config_class():
    env = os.environ.get('webapp_env'.upper(), 'dev').lower()
    if env == 'prod':
        return ProductionConfig
    return DevelopmentConfig


# CONF is a global variable to get settings via current_app.config(within Flask App Context)
CONF = get_config_class()
