"""The views for the user blueprint."""
from flask import Blueprint, render_template
from flask_login import login_required

import sys
import os
import dateutil
from datetime import datetime, timedelta
import inflection

blueprint = Blueprint(
    'user',
    __name__,
    url_prefix='/users',
    static_folder='../static'
)


@blueprint.route('/')
@login_required
def members():
    """Placeholder page for members only."""
    return render_template('users/members.html')


@blueprint.route('/foo')
@login_required
def foo_fn():
    """Placeholder page for members only."""
    return render_template('users/members.html')

#SO THERE REALLY NEEDS TO BE AN INTERMEDIARY STEP THAT COLLECTS THE ADDRESS AND LOGS THAT IN ADDITION TO THE REST


@blueprint.route('/chores/show_upcoming')
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
        #mark the current datetime, assign to now
        now = datetime.utcnow()
        #define a delta of 4 weeks
        until = now + timedelta(weeks=4)
        #generate a list of datetimes for each day in the next month
        month_of_days_dt = rrule(freq=DAILY, dtstart=now, until=until)
        #cast list of datetimes into human-friendly string format
        month_of_days = [day.strftime("%A, %B %d, %Y") for day in month_of_days_dt]
        #feed the template a month of days, and all chores for the logged in user. Jinja will display chores by day.
        # sys.stderr.write("USER NOT LOGGED IN (PYTHON, ROUTE:'/')\n")
        return render_template("dashboard.html", user=user, chores=chores, month=month_of_days)
    else:
        # sys.stderr.write("USER LOGGED IN (PYTHON, ROUTE:'/')")
        return render_template("homepage.html")


@blueprint.route('/newchore')
def createchore():
    """Render form to enter new chore for the household"""
    return render_template("newchore.html")


@blueprint.route('/newchore', methods=['POST'])
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


@blueprint.route('/takeachore', methods=['GET'])
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


@blueprint.route('/takechoreform', methods=['POST'])
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


@blueprint.route('/take_weekly_agreements', methods=['POST'])
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


@blueprint.route('/take_monthly_agreements', methods=['POST'])
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


@blueprint.route('/user-contributions.json')
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
