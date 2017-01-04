from jinja2 import StrictUndefined
from flask import Flask, jsonify, render_template, request, flash, redirect, session
from flask_login import LoginManager
from flask_debugtoolbar import DebugToolbarExtension
from model import connect_to_db, db, User, Address, Chore, Userchore
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY

import sys
import os
import dateutil
from datetime import datetime, timedelta
import inflect
import bcrypt
from social.apps.flask_app.routes import social_auth
from social.exceptions import SocialAuthBaseException

import dbwrangler, apiapijoyjoy, sys, helpers

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "S334R1T"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined
app.jinja_env.auto_reload=True
# app.register_blueprint(social_auth)

days_of_the_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
days_to_int = {'Monday':0, 'Tuesday':1, 'Wednesday':2, 'Thursday':3, 'Friday':4, 'Saturday':5, 'Sunday':6}

# SOCIAL_AUTH_USER_MODEL = 'model.User'

#### REMEMBERING SESSIONS
# SOCIAL_AUTH_FIELDS_STORED_IN_SESSION = ['keep']

# SOCIAL_AUTH_REMEMBER_SESSION_NAME = 'remember_me'

#### BEGIN ROUTES RELATING TO PYTHON-SOCIAL ####
# login_manager = LoginManager()

# @app.before_request
# def global_user():
#     g.user = get_current_logged_in_user
#     return

# @login_manager.user_loader
# def load_user(userid):
#     try:
#         return User.query.get(int(userid))
#     except (TypeError, ValueError):
#         pass


# @app.before_request
# def global_user():
#     g.user = login.current_user
#     return


# Make current user available on templates
# @app.context_processor
# def inject_user():
#     try:
#         return {'user': g.user}
#     except AttributeError:
#         return {'user': None}

#### END ROUTES RELATING TO PYTHON-SOCIAL ####

@app.route('/')
def index():
    """Homepage."""
    #if there's a user_id in our Flask session, use that to open the app to the user. Otherwise, send the user to a signup page

    if session.get('user_id', False):
        #show the user their upcoming chores
        #get the current user (email)
        user = dbwrangler.get_current_user()
        user_id = user.user_id
        #return a dictionary of one user's chores for a month, grouped by day
        chores = helpers.chores_by_date(user_id)
        print len(chores)
        #mark the current datetime, assign to now
        now = datetime.utcnow()
        #define a delta of 4 weeks
        until = now + timedelta(weeks=4)
        #generate a list of datetimes for each day in the next month
        month_of_days_dt = rrule(freq=DAILY, dtstart=now, until=until)
        #cast list of datetimes into human-friendly string format
        month_of_days = [day.strftime("%A, %B %d, %Y") for day in month_of_days_dt]
        #feed the template a month of days, and all chores for the logged in user. Jinja will display chores by day.
        return render_template("dashboard.html", user=user, chores=chores, month=month_of_days)
    else:
        return render_template("homepage.html")


@app.route('/login', methods=['POST'])
def login():
    """Process login"""
    # Get form variables
    email = request.form["email"]
    password = request.form["password"]
    #Check DB for user as asserted on form. Get details for that user from DB
    user = User.query.filter_by(email=email).first()

    #if the user isn't in the DB, redirect to login page, with a flash message to tell the user what's up
    #CAN I FORMAT THE FLASH MESSAGES IN BOOTSTRAP?
    if not user:
        flash("No such user, please try again!")
        return redirect("/login")
    #if the password given does not match the user password, return to login page with the password error message flashed to user
    if user.password != password:
        flash("Incorrect password")
        return redirect("/login")
    #if everything checks out, log the user in
    flash("Logged in")
    #Store userid pulled from db in Flask session
    session["user_id"] = user.email
    #Redirect to home page
    return redirect("/")

# @app.route("/tokensignin", methods=['POST'])
# def validate_via_google():
#     """WHAT IS THIS EVEN HERE FOR ???????"""
#     token = request.form.get("token")
#     print request.form.get
#     print apiapijoyjoy.validate_google_token(token)


@app.route('/signup', methods=['GET'])
def signup():
    """Display new user form"""
    return render_template("new_user.html")


@app.route('/signup', methods=['POST'])
def newuser():
    """Process new user"""
    #get details from form template
    email = request.form.get("email")
    password = request.form.get("password")
    name = request.form.get("name")
    lname = request.form.get("lname")

    #MOVE TO DBWRANGLER??? Create new user via SQLAlchemy with info from the form 
    new_user = User(email=email, password=password, name=name, lname=lname)

    #Start browser session for this user
    session["user_id"] = email

    #SQLAlchemy finalization of new db entry
    db.session.add(new_user)
    db.session.commit()

    #redirect to route to collect address and avatar
    return redirect("/more_info")

@app.route('/gtokensignin', methods=['POST'])
def check_google_token():
    """Take token from login, verify w/Google"""
    #get token from login page and google's token rigamorole
    gtoken = request.form.get("idtoken")
    #validate token
    g_profile = apiapijoyjoy.validate_google_token(gtoken)
    #collect user info from google
    name = g_profile['given_name']
    lname = g_profile['family_name']
    email = g_profile['email']
    # start a session
    session["user_id"] = email
    user = User.query.filter_by(email=email).first()
    #create flags for Flask to return to google's scripts and take frontend action accordingly
    if user:
        return "FLASK SEES USER"
    else:
        #create new user in SQLAlchemy using info above from Google. BUT WAIT WHAT?! CODE REVIEW PLS!
        new_user = User(email=email, name=name, lname=lname)
        db.session.add(new_user)
        db.session.commit()
        return "FLASK SEES NO USER"

@app.route("/user")
def user_profile():
    """Show user profile"""
    #get info for logged in user
    user = dbwrangler.get_current_user()
    #get housemates who live with this user
    all_housemates = User.query.filter_by(address=user.address).all()
    #get address info from DB
    address = Address.query.filter_by(address_id=user.address).first()
    #feed this data to the user page template for the user to review
    return render_template("user.html", 
                            user=user, 
                            address=address, 
                            all_housemates=all_housemates)

@app.route('/more_info')
def new_address():
    """Present new address form"""
    user = dbwrangler.get_current_user()
    if user:
        return render_template("new_user_more.html")
    else:
        return redirect("/")


@app.route('/complete_registration', methods=['POST'])
def process_address():
    """Add address to user account"""
    #get address info from form
    user_details = request.form
    #validate address with google geocoding
    update_details = apiapijoyjoy.validate_address(user_details)
    #update ino in db
    dbwrangler.newaddress(update_details)
    
    return redirect("/")


@app.route('/newchore')
def createchore():
    """Render form to enter new chore for the household"""
    return render_template("newchore.html")


@app.route('/newchore', methods=['POST'])
def newchore():
    """Request form contents to create new chore in db"""
    #get info from form template
    name = request.form.get('chore_name')
    description = request.form.get('chore_description')
    duration_hours = request.form.get('duration_hours') or 0
    duration_minutes = request.form.get('duration_minutes') or 0
    #compse duration in minutes
    duration_minutes = (int(duration_hours) * 60 + int(duration_minutes))
    occurance = request.form.get('occurance')
    comment = request.form.get('comment')
    by_time = request.form.get('by-time')
    days_weekly = request.form.getlist('days_weekly')
    date_monthly = request.form.get('date_monthly')
    #send chore details to DB
    dbwrangler.newchore(name, description, duration_minutes, occurance, by_time, 
                  comment, days_weekly, date_monthly)

    return redirect("/")


@app.route('/takeachore', methods=['GET'])
def claimchore():
    """Display a list of available chores and the days on which they occur, for 
    the user to select and claim"""
    user = dbwrangler.get_current_user()
    userchores = Userchore.query.filter_by(address_id=user.address, 
                                            commitment='INIT').all()
    #Below: chores that this belong to this user's address
    address_chores = [Chore.query.filter_by(chore_id=userchore.chore_id).first()
                                     for userchore in userchores]
    chores = []
    for chore in address_chores:
        #gather userchore entries for this chore
        userchores = Userchore.query.filter_by(chore_id=chore.chore_id).all()
        #isolate the item from ^ that is the clean (first) member of that chore inside userchores(table)
        base_userchore = [userchore for userchore in userchores if userchore.commitment == 'INIT']
        #get the rest of the chore data associated with that chore
        days_left = chore.days_weekly.split("|")
        days_left = helpers.find_days_left(chore, userchores, days_left)
        if len(days_left) != 0:
            chores.append(chore)
    for chore in chores:
        #recast the occurance dates for these as lists
        chore.days_weekly = chore.days_weekly.split("|")
        if chore.date_monthly:
            chore.date_monthly = inflect.engine().ordinal(chore.date_monthly)


    return render_template("takeachore.html", chores=chores, 
                            userchores=userchores, user=user)


@app.route('/takechoreform', methods=['POST'])
def feedjsboxes():
    """Get remaining days available for a chore and feed them to JS at takeachore.html"""

    form_chore_id = request.form.get("form_chore_id")

    #get the data in the association table that goes with the chore in the dropdown (as selected by the user). Ultimately want initial entry.
    userchores = Userchore.query.filter_by(chore_id=form_chore_id).all()

    base_userchore = [userchore for userchore in userchores if userchore.commitment == 'INIT']
    #isolate the item from the previous query results that is the clean (first) instance of that chore inside userchorees [above] and get the rest of the chore data associated with that chore from the chores table [below]
    base_chore = Chore.query.filter_by(chore_id=base_userchore[0].chore_id).first()

    #create a variable that will become the unclaimed instances of that chore, initialized as a list of all instances of that chore
    days_left = base_chore.days_weekly.split("|")

    #subtract off instances claimed already
    days_left = helpers.find_days_left(base_chore, userchores, days_left)

    return jsonify({'days_left': days_left,
                    'chore_id': base_chore.chore_id, 
                    'chore_name': base_chore.name,
                    'date_monthly': base_chore.date_monthly,
                    'occurance': base_chore.occurance})


@app.route('/take_weekly_agreements', methods=['POST'])
def take_weekly_agreements():
    """ Get agreed days from form and add them to userchores table in DB, 
        specific to daily and weekly chores"""

    #collect data from form template
    chore_id = request.form.get("chore_id")
    daysagreed = request.form.get("daysagreed")
    daysagreed = daysagreed.split("|")

    #no more unicode
    days_agreed = [str(i) for i in daysagreed]

    #recast agreements from T/F to days of the week (by name)
    days_agreed = [days_of_the_week[i] for i in range(7) if days_agreed[i] == 'true']

    #format list of daily agreements for addition to database (string)
    days_agreed = "|".join(days_agreed)    

    #save to database
    dbwrangler.add_commitment(days_agreed, chore_id)

    #redirect to form for further agreements
    return redirect("/takeachore")


@app.route('/take_monthly_agreements', methods=['POST'])
def take_monthly_agreements():
    """ Get agreed days from form and add them to userchores table in DB, 
        specific to monthly chores"""

    #collect data from form template
    chore_id = request.form.get("chore_id")
    date_monthly = request.form.get("date_monthly")

    #add agreements to database
    dbwrangler.add_commitment(date_monthly, chore_id)

    #redirect to form for further agreements
    return redirect("/takeachore")


@app.route('/user-contributions.json')
def user_contributions_chart():
    """Return a chart of data about household contributions."""

    #get current user according to Flask session
    user = dbwrangler.get_current_user()

    #get all users from the user table sharing their address (so, their housemates)
    all_housemates = User.query.filter_by(address=user.address).all()

    #calculate total minutes of labor wach month for the user and their housemates
    total_household_labor = dbwrangler.total_houehold_labor(user)

    #build a data dictionary to feed jsonify. First entry in the labels list is unclaied labor... total household labor from which we will subtract housemate contributions
    dd_labels = ["Unclaimed"]

    #dd_data will be the minutes per user. Instantiate as an empty list.
    dd_data = []

    #each user gets a unique color
    dd_bgcolors = helpers.color_picker(len(all_housemates)+1)

    #Chart.js lets you select bgcolor for each wedge as one hovers over the chart
    dd_hoverbg = ["#a6a6a6", "#a6a6a6","#a6a6a6","#a6a6a6"]

    leftover_labor = total_household_labor

    #build lists in each field of our data dictionary, with each member of the household at their own index
    for housemate in all_housemates:
        dd_labels.append(housemate.name)
        individual_labor = dbwrangler.individual_labor(housemate.user_id)
        dd_data.append(individual_labor)
        leftover_labor -= individual_labor

    #zeroth index is the unclaimed labor (this from 21 lines above)
    dd_data = [leftover_labor] + dd_data

    data_dict = {
                "labels": dd_labels, 
                "datasets":[{"data":dd_data, 
                "backgroundColor":dd_bgcolors, 
                "hoverBackgroundColor":dd_hoverbg}]
                }
                
    return jsonify(data_dict)

@app.route('/logout')
def logout():
    """Log out."""
    #delete the session key and value for user_id. Return user to homepage (with an emoty session dict)
    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")


# @app.errorhandler(500)
# def error_handler(error):
#     if isinstance(error, SocialAuthBaseException):
#         return redirect('/socialerror')

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app, os.environ.get("DATABASE_URL"))

    # login_manager.init_app(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)

    PORT = int(os.environ.get("PORT", 5000))

    app.run(host='0.0.0.0', debug=True, port=PORT)