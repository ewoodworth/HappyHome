from jinja2 import StrictUndefined

from flask import Flask, render_template, request, flash, redirect, session
from flask_debugtoolbar import DebugToolbarExtension

from model import connect_to_db, db, User, Address, Chore, Userchore

import dbwrangler, apiapijoyjoy, sys
#Consider grouping these by purpose

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
    session["user_id"] = user.email  #stores userid pulled from db in session
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

@app.route("/users/<int:user_id>")
def user_profile(user_id):
    """Show user profile"""

    user = User.query.get(user_id)
    return render_template("user.html", user=user)

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
    
    address_list = apiapijoyjoy.validate_address(address, apartment, 
                   city, state, zipcode)
    #this^ returns address_list
    dbwrangler.newaddress(address_list)
    
    return redirect("/")

@app.route('/accept_address')
def accept_address():
    user_id = session["user_id"]
    user = User.query.filter_by(email=user_id).first()

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
    if by_time:
            by_time = datetime.datetime.strptime(str(by_time), "%H:%M"),
    else:
            by_time = None
    days_weekly = request.form.getlist('days_weekly')
    date_monthly = request.form.get('date_monthly')
    #save day data as pipe-joined string
    if occurance == 'daily':
        days_weekly = "Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday"
    elif occurance == 'weekly':
        days_weekly = "|".join(days_weekly)
    print days_weekly
    chore_list = [name, description, duration_minutes, occurance, by_time, 
                  comment, days_weekly, date_monthly]

    dbwrangler.newchore(chore_list)

    return redirect("/")

@app.route('/takeachore', methods=['GET'])
def claimchore():
    """Claim a chore"""
    user_id = session["user_id"]
    user = User.query.filter_by(email=user_id).first()
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
    base_userchore = [userchore for userchore in userchores if userchore.commitment == 'INIT']
    base_chore = Chore.query.filter_by(chore_id=base_userchore[0].chore_id).first()
    print "THE BASE CHORE IN PLAY IS:", base_chore
    base_chore_freq = base_chore.days_weekly
    print "THE FREQUENCY OF THIS CHORE IS", base_chore_freq
    days_left = base_chore.days_weekly
    for item in days_left:
            print item
    days_left_list = [item for item in set(days_left)]
    print (days_left_list) #from ints left delete indexes matching numerals in commitment POPOPOP
    # intsleft = str(intsleft) #UNICODE IS NOT MY FRIEND
    for chore in userchores:
        chore.commitment = str(chore.commitment)
        if chore.commitment == 'INIT':
            pass
        elif chore.commitment:
            for char in chore.commitment:
                print char
                intsleft = intsleft.pop(int(char))
                print intsleft
    return intsleft  ###ALL THIS STUFF

@app.route('/takeagreements', methods=['POST'])
def takeagreements():
    """ Get agreed days from form and add them to userchores table in DB"""
    chore_id = request.form.get("chore_id")
    daysagreed = request.form.get("daysagreed")
    daysagreed = daysagreed.split(",")
    days_agreed = ""
    for i in range(7):
        if daysagreed[i] == 'true':
            days_agreed = days_agreed + str(i)
        else:
            pass
    dbwrangler.add_commitment(days_agreed, chore_id)
    return redirect("/takeachore")

@app.route('/logout')
def logout():
    """Log out."""

    del session["user_id"]
    flash("Logged Out.")
    return redirect("/")


@app.route('/upcomingchores')
def viewchore():
    """See upcoming chores"""
    user_id = session["user_id"]
    user = User.query.filter_by(email=user_id).first()
    #return all chores at this address
    userchores = Userchore.query.filter_by(address_id=user.address, 
                    commitment='INIT').all()
    chores = [Chore.query.filter_by(chore_id=userchore.chore_id).first() 
                for userchore in userchores]

    return render_template("upcomingchores.html", chores=chores)

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