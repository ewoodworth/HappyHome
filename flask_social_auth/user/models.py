"""User models."""
import datetime as dt
import os
import sys

sys.path.append('/home/vagrant/src/HappyHome/env/lib/python2.7/site-packages')
sys.path.append('/home/vagrant/src/HappyHome/flask_social_auth')

from flask_login import UserMixin
from sqlalchemy.orm import relationship, backref
from flask_sqlalchemy import SQLAlchemy
# from app import app
from extensions import db, bcrypt


class Role(db.Model):

    """User roles."""

    __tablename__ = 'roles'

    id = db.Column(db.Integer, primary_key=True)  # pylint: disable=redefined-builtin,invalid-name
    name = db.Column(db.String(80), unique=True, nullable=False)
    user_id = db.Column(db.ForeignKey('users.id'), nullable=True)
    user = relationship('User', backref='roles')

    def __init__(self, name, **kwargs):
        """Init the role."""
        db.Model.__init__(self, name=name, **kwargs)

    def __repr__(self):
        """repr."""
        return '<Role({name})>'.format(name=self.name)


class User(UserMixin, db.Model):

    """The user model."""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)  # pylint: disable=redefined-builtin,invalid-name
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=True)  # the hashed password
    created_at = db.Column(db.DateTime, nullable=False, default=dt.datetime.utcnow)
    first_name = db.Column(db.String(100), nullable=True)
    last_name = db.Column(db.String(100), nullable=True)
    active = db.Column(db.Boolean(), default=False)
    phone_number = db.Column(db.String(15), nullable=True)
    avatar_src = db.Column(db.String(30), nullable=True)
    address = db.Column(db.Integer, db.ForeignKey('addresses.id'), 
              nullable=True)
    # chores = db.relationship('Chore',
    #                      secondary=userchores,
    #                      backref='users')


    def __init__(self, username, email, password=None, **kwargs):
        """Init the user name."""
        db.Model.__init__(self, username=username, email=email, **kwargs)
        if password:
            self.set_password(password)
        else:
            self.password = None

    @classmethod
    def get_by_id(cls, _id):
        """Get the user by ``_id``."""
        can_to_int = any(
            (isinstance(_id, str) and _id.isdigit(),
             isinstance(_id, (int, float))),
        )
        if can_to_int:
            return cls.query.get(int(_id))
        return None

    def set_password(self, password):
        """Set the password."""
        self.password = bcrypt.generate_password_hash(password)

    def check_password(self, value):
        """Validate the password."""
        return bcrypt.check_password_hash(self.password, value)

    @property
    def full_name(self):
        """Combine first_name and last_name."""
        return "{0} {1}".format(self.first_name, self.last_name)

    def __repr__(self):
        """repr."""
        return '<User({username!r})>'.format(username=self.username)

class Address(db.Model):
    """Addresses for users of website."""

    __tablename__ = "addresses"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    apartment = db.Column(db.String(6), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    standard_address = db.Column(db.String(150), nullable=True)
    address_street_num = db.Column(db.String(10), nullable=True)
    address_street = db.Column(db.String(50), nullable=True)
    address_city = db.Column(db.String(50), nullable=True)
    address_state = db.Column(db.String(2), nullable=True)
    address_zip = db.Column(db.String(50), nullable=True)


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Address address_id=%s address=%s>" % (self.id, self.standard_address)


class Chore(db.Model):
    """Chore on website."""

    __tablename__ = "chores"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    duration_minutes = db.Column(db.Integer, nullable=False)
    occurance = db.Column(db.String(10), nullable=True)
    days_weekly = db.Column(db.String, nullable=True)
    date_monthly = db.Column(db.Integer, nullable=True)
    by_time = db.Column(db.Time, nullable=True)
    comment = db.Column(db.String(15), nullable=True)

    def monthly_labor_hours(self):
        """Returns time(min) per month for a given chore"""
        if self.occurance == 'daily':
            monthly_hours = self.duration_minutes * 30
        elif self.occurance == 'weekly':
            monthly_hours = len(self.days_weekly.split("|")) * 4 * self.duration_minutes
        elif self.occurance == 'monthly':
            monthly_hours = self.duration_minutes
        return (monthly_hours)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Chore chore_id=%s name=%s>" % (self.id, self.name)


class Userchore(db.Model):
    """Association table for users and chores."""

    __tablename__ = "userchores"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), 
              nullable=False)
    chore_id = db.Column(db.Integer, db.ForeignKey('chores.id'), 
              nullable=False)
    address_id= db.Column(db.Integer, db.ForeignKey('addresses.id'), 
              nullable=False)
    #Consider making default=2.5 rather than nullable
    rating = db.Column(db.Integer, nullable=True)
    commitment = db.Column(db.String(50), nullable=True)

    # Define relationship to foreign keys in other tables
    user = relationship("User", backref=backref('users'))
    chore = relationship("Chore", backref=backref('chores'))
    address = relationship("Address", backref=backref('addresses'))

    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Userchore uc_id=%s user_id=%s task_id=%s address_id=%s rating=%s commitment=%s>" % (self.uc_id, 
                self.user_id , self.chore_id , self.address_id, self.rating, 
                self.commitment)

# # # # # # # # # # # #
#START FLASK SQLAlchemy CONFIGURATION CLASSES
# # # # # # # # # # # #
class Config:
    SECRET_KEY = 'development key'
    ADMINS = frozenset(['THIS WILL BE MY EMAIL', ])


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'postgresql:///happyhome'

class ProductionConfig(Config):
    SECRET_KEY = 'Prod key'
    db_uri = os.environ.get('DATABASE_URL', None)
    SQLALCHEMY_DATABASE_URI = db_uri


config = { 
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}



##############################################################################
# Helper functions
#COPIED FROM HB PROJECT< SEE IF THEY"RE STILL NEEDED WITH FULL FLASK SUPPORT

# def connect_to_db(app, db_uri=None):
#     """Connect the database to our Flask app."""
#     # Configure to use our PostgreSQL database
#     if not db_uri and 'DATABASE_URL' in os.environ:
#         db_uri = os.environ['DATABASE_URL']
#     app.config['SQLALCHEMY_DATABASE_URI'] = db_uri or 'postgresql:///happyhome'
#     app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
#     app.config['SQLALCHEMY_ECHO'] = True

#     db.app = app
#     db.init_app(app)
    
# if __name__ == "__main__":
#     # As a convenience, if we run this module interactively, it will leave
#     # you in a state of being able to work with the database directly.
#     connect_to_db(app)
#     print "Connected to DB."
