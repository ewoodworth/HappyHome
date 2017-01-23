"""Model factories."""
from factory import PostGenerationMethodCall, Sequence
from factory.alchemy import SQLAlchemyModelFactory
from flask_social_auth.app import db
from flask_social_auth.user.models import User


class BaseFactory(SQLAlchemyModelFactory):

    """Base factory for used for all other factories."""

    class Meta:
        abstract = True
        sqlalchemy_session = db.session


class UserFactory(BaseFactory):

    """Create users for testing."""

    username = Sequence(lambda n: "user{0}".format(n))
    email = Sequence(lambda n: "user{0}@example.com".format(n))
    password = PostGenerationMethodCall('set_password', 'example')
    active = True

    class Meta:
        model = User
