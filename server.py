from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Address, Chore, UserChores

import requests


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "S33KR1T"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined
app.jinja_env.auto_reload=True

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

@app.route('/add_address', methods=['POST'])
def add_address():
    """Add address to user account"""
    # Get form variables
    address = request.form.get["address"]  #switch these over to .get
    apartment = request.form.get["apartment"]
    city =  request.form.get["city"]
    state =  request.form.get["state"]
    zipcode = request.form.get["zipcode"]

    geocode_string = address +" "+ city +" "+ state +" "+ zipcode

    #Make google give me a JSON object
    #parse JSON for latitutde and longitude
    google_key = os.environ['GOOGLE_GEOCODING_KEY']
    new_address = Address(address=address, apartment=apartment, city=city,
                  state=state, zipcode=zipcode)

    r = requests.get(
    "https://maps.googleapis.com/maps/api/geocode/json?address="+new_address+"&key="+google_key)

    address_jsom = r.json()



    

    ##Sooo... how do I make a JSON object?    
    # 
    # ## ASSEMBLE ADDRESS IN THE FORMAT THAT GOOGLE MAPS NEEDS IT, GET LAT/LONG
    # https://www.googleapis.com/geolocation/v1/geolocate?key=YOUR_API_KEY 
    # http://maps.googleapis.com/maps/api/geocode/outputFormat?parameters

    ## FOR THAT ADDRESS
    ## SEEK THAT ADDRESS IN DB
    ## IF FOUND VERIFY W/USER
    ## USER SAYS YES OR VERIFY
    return redirect("/")

@app.route('/newchore', methods=['GET'])
def createchore():
    """Create a new task for your household"""
    return render_template("createchore.html")

@app.route('/newchore', methods=['POST'])
def newchore():
    """Process new chore"""
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