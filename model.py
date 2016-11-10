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
    chores = db.relationship("Chore",
                         secondary="userchores",
                         backref="users")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<User user_id=%s email=%s>" % (self.user_id, self.email)


class Address(db.Model):
    """Addresses for users of website."""

    __tablename__ = "addresses"

    address_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    apartment = db.Column(db.String(6), nullable=True)
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
    duration_minutes = db.Column(db.String(20), nullable=False)
    frequency = db.Column(db.String(30), nullable=False)

    ##WRITE METHOD TO CAST DAYS OF THE WEEK IN FREQ AS LIST
    def dayify_frequency(self):
        """Takes the frequency field (chore.frequency=[d/w/m, numdays, time, 
            any/morning/evening]) and splits it into a list)"""
        self.frequency = (self.frequency).split("|")
        if self.frequency[0] == 'daily' or self.frequency[0] == 'weekly':
            self.frequency[1] = [str(char) for char in self.frequency[1]]

    # users = db.relationship("User",
    #                     secondary="userchores",
    #                     backref="chores")

    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Chore chore_id=%s name=%s>" % (self.chore_id, self.name)


class Userchore(db.Model):
    """Association table for users and chores."""

    __tablename__ = "userchores"

    uc_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), 
              nullable=False)
    task_id = db.Column(db.Integer, db.ForeignKey('chores.chore_id'), 
              nullable=False)
    address_id= db.Column(db.Integer, db.ForeignKey('addresses.address_id'), 
              nullable=False)
    #Consider making default=2.5 rather than nullable
    rating = db.Column(db.Integer, nullable=True)
    commitment = db.Column(db.String(50), nullable=True)

    # Define relationship to addresses
    address = db.relationship("Address",
                            backref=db.backref("userchores", order_by=uc_id))

    def __repr__(self):
        """Provide helpful representation when printed."""
        return "<Userchore uc_id=%s user_id=%s task_id=%s address_id=%s rating=%s commitment=%s>" % (self.uc_id, 
                self.user_id , self.task_id , self.address_id, self.rating, 
                self.commitment)
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