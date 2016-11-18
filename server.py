from jinja2 import StrictUndefined

from flask import Flask, jsonify, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Address, Chore, Userchore

import dbwrangler, apiapijoyjoy, sys, helpers

from dateutil.relativedelta import *
from dateutil.rrule import *
from datetime import datetime

import pprint

#Consider grouping these by purpose

app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "S33KR1T"

# Normally, if you use an undefined variable in Jinja2, it fails silently.
# This is horrible. Fix this so that, instead, it raises an error.
app.jinja_env.undefined = StrictUndefined
app.jinja_env.auto_reload=True

days_of_the_week = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
days_to_int = {'Monday':0, 'Tuesday':1, 'Wednesday':2, 'Thursday':3, 'Friday':4, 'Saturday':5, 'Sunday':6}


@app.route('/')
def index():
    """Homepage."""
    if session.get('user_id', False):
        user = dbwrangler.get_current_user()
        user_id = user.user_id
        #return all chores at this address
        chores = helpers.chores_by_date(user_id)
        now = datetime.utcnow()
        until = now + relativedelta(months=+1)
        month_of_days_dt = rrule(DAILY,dtstart=now,until=until)
        month_of_days = [day.strftime("%A, %B %d, %Y") for day in month_of_days_dt]
        print month_of_days
        pprint.pprint(chores)
        return render_template("dashboard.html", user=user, chores=chores, month=month_of_days)
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
    session["user_id"] = user.email  #stores userid pulled from db in session
    return redirect("/")

@app.route("/takefbuser", methods=['POST'])
def take_fb_user():
    """Take in user from FB Login"""
    print request.form.get("authResponse[userID]")
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


@app.route("/user")
def user_profile():
    """Show user profile"""
    user = dbwrangler.get_current_user()
    address = Address.query.filter_by(address_id=user.address).first()
    userchores = Userchore.query.filter_by(address_id=user.address, commitment='INIT').all()
    chore_ids = [userchore.chore_id for userchore in userchores]
    total_labor_minutes = 0
    for item in chore_ids:
        chore = Chore.query.filter_by(chore_id=item).first()
        # monthly labor hours for this exact chore
        if chore.occurance == 'daily':
            monthly_minutes = int(chore.duration_minutes) * 30
        elif chore.occurance == 'weekly':
            monthly_minutes = len(chore.days_weekly.split("|")) * 4 * int(chore.duration_minutes)
        elif chore.occurance == 'monthly':
            monthly_minutes  = int(chore.duration_minutes)
        total_labor_minutes = total_labor_minutes + monthly_minutes
    return render_template("user.html", user=user, address=address)


@app.route('/add_address')
def new_address():
    """Present new address form"""
    return render_template("joinhousehold.html")


@app.route('/process_address', methods=['POST'])
def process_address():
    """Add address to user account"""                
    address = request.form.get("address")
    apartment = request.form.get("apartment")
    city =  request.form.get("city")
    state =  request.form.get("state")
    zipcode = request.form.get("zipcode")
    address_list = apiapijoyjoy.validate_address(address, city, state, zipcode, apartment)
    dbwrangler.newaddress(address_list)
    
    return redirect("/")


@app.route('/newchore')
def createchore():
    """Render form to enter new chore for the household"""
    return render_template("newchore.html")


@app.route('/newchore', methods=['POST'])
def newchore():
    """Process new chore"""
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

    dbwrangler.newchore(name, description, duration_minutes, occurance, by_time, 
                  comment, days_weekly, date_monthly)

    return redirect("/")


@app.route('/takeachore', methods=['GET'])
def claimchore():
    """Claim a chore"""
    ##FFEED THE LIST OF CHORES IN SUCH A WAY AS YOU CAN DISPLAY THEM CHRONOLOGICALLY

    user = dbwrangler.get_current_user()
    userchores = Userchore.query.filter_by(address_id=user.address, 
                                            commitment='INIT').all()
    chores = [Chore.query.filter_by(chore_id=userchore.chore_id).first()
                                     for userchore in userchores]
    for chore in chores:
        chore.days_weekly = chore.days_weekly.split("|")

    return render_template("takeachore.html", chores=chores, 
                            userchores=userchores, user=user)


@app.route('/takechoreform', methods=['POST'])
def feedjsboxes():
    """Get remaining days available for a chore and feed them to JS at takeachore.html"""
    form_chore_id = request.form.get("form_chore_id")
    userchores = Userchore.query.filter_by(chore_id=form_chore_id).all()
    #isolate the item from ^ that is the clean (first) member of that chore inside userchores(table)
    base_userchore = [userchore for userchore in userchores if userchore.commitment == 'INIT']
    #get the rest of the chore data associated with that chore
    base_chore = Chore.query.filter_by(chore_id=base_userchore[0].chore_id).first()
    days_left = base_chore.days_weekly.split("|")
    days_left = helpers.find_days_left(base_chore, userchores, days_left)

    return jsonify({'days_left': days_left,
                    'chore_id': base_chore.chore_id, 
                    'chore_name': base_chore.name,
                    'date_monthly': base_chore.date_monthly,
                    'occurance': base_chore.occurance})


@app.route('/take_weekly_agreements', methods=['POST'])
def take_weekly_agreements():
    """ Get agreed days from form and add them to userchores table in DB"""
    chore_id = request.form.get("chore_id")
    daysagreed = request.form.get("daysagreed")
    daysagreed = daysagreed.split("|")
    days_agreed = [str(i) for i in daysagreed] #No more unicode
    days_agreed = [days_of_the_week[i] for i in range(7) if days_agreed[i] == 'true'] #Cast days from true to dayname
    days_agreed = "|".join(days_agreed)    

    dbwrangler.add_commitment(days_agreed, chore_id)

    return redirect("/takeachore")


@app.route('/take_monthly_agreements', methods=['POST'])
def take_monthly_agreements():
    """ Get agreed days from form and add them to userchores table in DB"""
    chore_id = request.form.get("chore_id")
    date_monthly = request.form.get("date_monthly")

    dbwrangler.add_commitment(date_monthly, chore_id)

    return redirect("/takeachore")


@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")


@app.route('/user-contributions.json')
def user_contributions_chart():
    """Return a chart of data about household contributions."""
    user = dbwrangler.get_current_user()
    all_housemates = User.query.filter_by(address=user.address).all()
    total_household_labor = dbwrangler.total_houehold_labor(user)
    dd_labels = ["Unclaimed"]
    dd_data = []
    dd_bgcolors = helpers.color_picker(len(all_housemates)+1)
    dd_hoverbg = ["#a6a6a6", "#a6a6a6","#a6a6a6","#a6a6a6"]
    for housemate in all_housemates:
        dd_labels.append(housemate.name)
        individual_labor = dbwrangler.individual_labor(housemate.user_id)
        dd_data.append(individual_labor)
        leftover_labor = [total_household_labor - individual_labor]
    for housemate in all_housemates:
        print "{} is committing to {} minutes of the household labor".format(housemate.name, individual_labor)
    dd_data = [leftover_labor] + dd_data
    data_dict = {
                "labels": dd_labels, 
                "datasets":[{"data":dd_data, 
                "backgroundColor":dd_bgcolors, 
                "hoverBackgroundColor":dd_hoverbg}]
                }

    return jsonify(data_dict)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the point
    # that we invoke the DebugToolbarExtension

    # Do not debug for demo
    app.debug = True

    connect_to_db(app)
    # Use the DebugToolbar
    DebugToolbarExtension(app)

    app.run(host='0.0.0.0', debug=True)