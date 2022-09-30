import click
from flask import current_app
from flask.cli import FlaskGroup, run_command

from webapp import create_app, config
from webapp.extensions import db
from webapp.utils import pretty_print
from webapp.cli.shell_ipython import shell_command


def create(group):
    app = current_app or create_app()
    group.app = app
    return app


@click.group(cls=FlaskGroup, add_default_commands=False, create_app=create)
def manager():
    pass


@manager.command()
def resetdb():
    db.drop_all()
    db.engine.execute('DROP TABLE IF EXISTS alembic_version')


manager.add_command(run_command, 'run')
manager.add_command(run_command, 'runserver')
manager.add_command(shell_command, 'shell')
