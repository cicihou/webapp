import logging
import os
import datetime


class Config(object):
    # noinspection PyPackageRequirements
    DEBUG = False

    LOG_FORMAT = '%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    LOG_LEVEL = logging.INFO

    # Flask-SQLAlchemy settings
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:mysql1234@localhost/webapp?charset=utf8mb4'
    SQLALCHEMY_POOL_RECYCLE = 3600
    SQLALCHEMY_POOL_SIZE = 5
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    BCRYPT_SALT = b'$2b$12$Hw4dlmptnnOJ4RdCyimiVO'


class DevelopmentConfig(Config):
    DEBUG = True

    SQLALCHEMY_ECHO = False


class ProductionConfig(Config):
    LOG_LEVEL = logging.WARNING


def get_config_class():
    env = os.environ.get('webapp_env'.upper(), 'dev').lower()
    if env == 'prod':
        return ProductionConfig
    return DevelopmentConfig


# CONF is a global variable to get settings via current_app.config(within Flask App Context)
CONF = get_config_class()
