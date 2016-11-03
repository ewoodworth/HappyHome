"""Models and database functions for final project."""
import heapq
import time
from flask_sqlalchemy import SQLAlchemy
# import correlation

# This is the connection to the PostgreSQL database; we're getting this through
# the Flask-SQLAlchemy helper library. On this, we can find the `session`
# object, where we do most of our interactions (like committing, etc.)

db = SQLAlchemy()


##############################################################################
# Model definitions
class User(db.Model):
    """User of website."""

    __tablename__ = "users"

    user_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    email = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(25), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    phone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.Integer, db.ForeignKey('addresses.address_id'), 
              nullable=True)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class Address(db.Model):
    """Addresses for users of website."""

    __tablename__ = "addresses"

    address_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    apartment = db.Column(db.String(6), nullable=True)
    city = db.Column(db.String(35), nullable=False)
    state = db.Column(db.String(2), nullable=False)
    zipcode = db.Column(db.String(5), nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    standard_address = db.Column(db.String(150), nullable=True)


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Address address_id=%s address=%s>" % (self.address_id, self.address)


class Chore(db.Model):
    """Chore on website."""

    __tablename__ = "chores"

    chore_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(150), nullable=False)
    duration = db.Column(db.String(20), nullable=False)
    frequency = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Chore chore_id=%s name=%s>" % (self.chore_id, self.name)


class UserChores(db.Model):
    """Association table for users and chores."""

    __tablename__ = "userchores"

    uc_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), 
              nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('chores.chore_id'), 
              nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    commitment = db.Column(db.String(50), nullable=False)

    # Define relationship to user
    user = db.relationship("User",
                           backref=db.backref("userchores", order_by=uc_id))

    # Define relationship to task
    chore = db.relationship("Chore",
                            backref=db.backref("userchores", order_by=uc_id))

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Rating rating_id=%s movie_id=%s user_id=%s score=%s>" % (
            self.rating_id, self.movie_id, self.user_id, self.score)


##############################################################################
# Helper functions

def connect_to_db(app):
    """Connect the database to our Flask app."""

    # Configure to use our PostgreSQL database
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///happyhome'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.config['SQLALCHEMY_ECHO'] = True
    
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # As a convenience, if we run this module interactively, it will leave
    # you in a state of being able to work with the database directly.

    from server import app
    connect_to_db(app)
    print "Connected to DB."
