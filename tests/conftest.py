"""Defines fixtures available to all tests."""
import pytest
from flask_social_auth.app import create_app
from flask_social_auth.app import db as _db
from flask_social_auth.settings import TestConfig

from .factories import UserFactory


@pytest.yield_fixture(scope='function')
def app():
    """Flask app fixture."""
    _app = create_app(TestConfig)
    ctx = _app.test_request_context()
    ctx.push()

    yield _app

    ctx.pop()


@pytest.yield_fixture(scope='function')
def db(app):
    """DB fixture."""
    _db.app = app
    with app.app_context():
        _db.create_all()

    yield _db

    _db.drop_all()


@pytest.fixture
def user(db):
    """User fixture."""
    user = UserFactory(password='myprecious')
    db.session.commit()
    return user
