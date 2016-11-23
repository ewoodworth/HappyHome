"""Models and database functions for final project."""


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
    email = db.Column(db.String(50), nullable=True)
    fb_id =  db.Column(db.String(50), nullable=True)
    password = db.Column(db.String(25), nullable=True)
    name = db.Column(db.String(50), nullable=True)
    lname = db.Column(db.String(50), nullable=True)
    phone_number = db.Column(db.String(15), nullable=True)
    avatar_src = db.Column(db.String(30), nullable=True)
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
    address_street_num = db.Column(db.String(10), nullable=True)
    address_street = db.Column(db.String(50), nullable=True)
    address_city = db.Column(db.String(50), nullable=True)
    address_state = db.Column(db.String(2), nullable=True)
    address_zip = db.Column(db.String(50), nullable=True)


    def __repr__(self):
        """Provide helpful representation when printed."""

        return "<Address address_id=%s address=%s>" % (self.address_id, self.standard_address)


class Chore(db.Model):
    """Chore on website."""

    __tablename__ = "chores"

    chore_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
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

        return "<Chore chore_id=%s name=%s>" % (self.chore_id, self.name)


class Userchore(db.Model):
    """Association table for users and chores."""

    __tablename__ = "userchores"

    uc_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), 
              nullable=False)
    chore_id = db.Column(db.Integer, db.ForeignKey('chores.chore_id'), 
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
                self.user_id , self.chore_id , self.address_id, self.rating, 
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