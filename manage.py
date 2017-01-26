#!/usr/bin/env python
import os
import sys

sys.path.append('/home/vagrant/src/HappyHome/env/lib/python2.7/site-packages')

from flask_script import Manager, Server, Shell
from flask_social_auth.app import create_app
from flask_social_auth.extensions import db
from flask_social_auth.settings import DevConfig
from flask_social_auth.user.models import User

# import config

app = create_app(DevConfig)

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_PATH = os.path.join(HERE, 'tests')

manager = Manager(app)


def _make_context():
    """Return context dict for a shell session so you can access
    app, db, and the User model by default.
    """
    return {'app': app, 'db': db, 'User': User}


@manager.command
def test():
    """Run the tests."""
    import pytest
    exit_code = pytest.main([TEST_PATH, '--verbose'])
    return exit_code


@manager.command
def syncdb():
    from social.apps.flask_app.default import models
    User.metadata.create_all(db.engine)
    models.PSABase.metadata.create_all(db.engine)

manager.add_command('server', Server(host='0.0.0.0'))
manager.add_command('shell', Shell(make_context=_make_context))

if __name__ == '__main__':
    manager.run()
