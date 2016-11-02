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

    return redirect("/process_address")

@app.route('/add_address')
def new_address():
    """Present new address form"""
    return render_template("joinhousehold.html")

@app.route('/process_address', methods=['POST'])
def process_address():
    """Add address to user account"""
    # Get form variables
    address = request.form.get["address"]
    #prep address for inclusion in API query
    address = address.replace(" ", "+")
    apartment = request.form.get["apartment"]
    city =  request.form.get["city"]
    state =  request.form.get["state"]
    zipcode = request.form.get["zipcode"]
    #concatenate user input for API query
    geocode_string = address +"+"+ city +"+"+ state +"+"+ zipcode
    google_key = os.environ['GOOGLE_GEOCODING_KEY']
    #Make google give me a JSON object
    r = requests.get(
    "https://maps.googleapis.com/maps/api/geocode/json?address="+new_address+"&key="+google_key)
    address_json = r.json()
    #parse JSON for latitutde and longitude
    standard_address = address_json[u'results'][0][u'formatted_address']
    #If needed later there are smaller pixels of address data in the JSON objects
    latitude = address_json[u'results'][0][u'geometry'][u'location'][u'lat']
    longitude = address_json[u'results'][0][u'geometry'][u'location'][u'lng']


    ## SEEK THAT ADDRESS IN DB
    ## IF FOUND VERIFY W/USER
    ## USER SAYS YES OR VERIFY
    return redirect("/")

@app.route CONFIRM ADDRESS
@app.route FAIL CONFIRMATION

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