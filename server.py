from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Address, Chore, Userchore

import requests

import random

import os


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "S33KR1T"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined
app.jinja_env.auto_reload=True


def genkey(n):
    """Generate a pseudorandom n-digit key"""
    randkey=""
    seedstring="01234567890!@#$%^&*()_+~{}|:<>?QWERTYUIOPASDFGHJKLZXCVNBM<>qwertyuiopasdfhgjklzxcvbnm"
    for i in range(n):
        rando = random.choice(seedstring)
        randkey = randkey+rando
    return randkey

@app.route('/')
def index():
    """Homepage."""
    if session.get('user_id', False):
        return render_template("dashboard.html")
    else:
        return render_template("homepage.html")

@app.route('/login', methods=['POST'])
def login():
    """Process login"""
    # Get form variables
    email = request.form["email"]
    password = request.form["password"]

    user = User.query.filter_by(email=email).first()

    if not user:
        flash("No such user")
        return redirect("/login")

    if user.password != password:
        flash("Incorrect password")  #Would prefer errors in div using javascript
        return redirect("/login")

    flash("Logged in")
    session["user_id"] = user.user_id  #stores userid pulled from db in session
    return redirect("/")

@app.route('/signup', methods=['GET'])
def signup():
    """Display new user form"""
    return render_template("createuser.html")

@app.route('/signup', methods=['POST'])
def newuser():
    """Process new user"""

    email = request.form["email"]
    password = request.form["password"]
    name = request.form["name"]
    phone_number = request.form["phone_number"]

    new_user = User(email=email, password=password, name=name, 
               phone_number=phone_number)

    session["user_id"] = email #Start browser session

    db.session.add(new_user)
    db.session.commit()

    return redirect("/add_address")

@app.route('/add_address')
def new_address():
    """Present new address form"""
    return render_template("joinhousehold.html")

@app.route('/process_address', methods=['POST'])
def process_address():
    """Add address to user account"""
    #prep address for inclusion in API query                    
    address = request.form.get("address")
    apartment = request.form.get("apartment")
    city =  request.form.get("city")
    state =  request.form.get("state")
    zipcode = request.form.get("zipcode")
    #concatenate user input for API query
    address = address.replace(" ", "+")
    geocode_string = address +"+"+ city +"+"+ state +"+"+ zipcode
    google_key = os.environ['GOOGLE_MAPS_GEOCODING']
    #Make google give me a JSON object
    r = requests.get(
    "https://maps.googleapis.com/maps/api/geocode/json?address="+geocode_string+"&key="+google_key)
    address_json = r.json()
    #parse JSON for latitutde and longitude
    latitude = address_json[u'results'][0][u'geometry'][u'location'][u'lat']
    longitude = address_json[u'results'][0][u'geometry'][u'location'][u'lng']
    standard_address = address_json[u'results'][0][u'formatted_address']
    #See if the address is already here, if not, add it
    address = Address.query.filter_by(standard_address=standard_address, 
              apartment=apartment).first()
    if not address:
        address =  Address(standard_address=standard_address, latitude=latitude, 
                       longitude=longitude, apartment=apartment)
        db.session.add(new_address)
        db.session.commit()
    user = User.query.filter_by(email=session["user_id"]).first()
    user.address = address.address_id
    db.session.commit()
    return redirect("/")

@app.route('/accept_address')
def accept_address():
    user_id = session["user_id"]
    user = User.query.filter_by(email=user_id).first()

@app.route('/newchore')
def createchore():
    """Create a new task for your household"""
    return render_template("newchore.html")

@app.route('/newchore', methods=['POST'])
def newchore():
    """Process new chore"""
    name = request.form.get("chore_name")
    description = request.form.get("chore_description")
    duration_hours = request.form.get("duration_hours")
    duration_minutes = request.form.get("duration_minutes")
    #Are these conditionals the best way to deal with null/None in form data?
    if duration_hours:
        duration_minutes = (int(duration_hours) * 60 + int(duration_minutes))
    else:
        duration_minutes = int(duration_minutes)
    everyday = request.form.get("everyday")
    dayofweek = request.form.get("dayofweek")
    date = request.form.get("date")
    if everyday:
        frequency = "daily"
    elif dayofweek:
        frequency = dayofweek
    elif date:
        frequency = "monthly "+date
    by_hour = request.form.get("by_hour")
    by_min = request.form.get("by_min")
    ampm = request.form.get("ampm")
    by_time = ""
    #^This may come back to bite me!!!
    if ampm:
        by_time = ampm
    if by_min:
        by_time = by_min + by_time
    if by_hour:
        by_time = by_hour + by_time
    #Sooo... what if I slip a string field in postgres, an integer. Whose typing wins?
    new_chore =  Chore(name=name, description=description, duration_minutes=duration_minutes, 
                 frequency=frequency , by_time = by_time)
    db.session.add(new_chore)
    db.session.commit()
    user = User.query.filter_by(email=session["user_id"]).first()
    new_userchore = Userchore(user_id=user.user_id, address_id=user.address, task_id=new_chore.chore_id)

    return redirect("/")

@app.route('/acceptchore')
def claimchore():
    """Claim responsibility for a chore"""
    return render_template("claimchore.html")


#things to paste later
# <input type="text" name="" placeholder="" required>
#
#



if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)
    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host='0.0.0.0', debug=True)