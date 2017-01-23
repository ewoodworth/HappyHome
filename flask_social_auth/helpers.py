from flask import session
from model import User, Address, Chore, Userchore

# from dateutil.relativedelta import relativedelta
from dateutil.rrule import rrule, DAILY, WEEKLY, MONTHLY
from datetime import datetime, timedelta
import requests
import os


MY_COLOR_FAMILY = ['#CE93D8', '#B39DDB', '#9FABDA', '#90CAF9', '#81d4fa', '#8ddeea', 
                   '#80cbc4', '#a5d6a7', '#c5e1a5', '#BA68C8', '#9575CD', '#7986CB',
                   '#64b5f6', '#4fc3f7', '#4dd0e1', '#4db6ac', '#81c784', '#aed581',
                   '#AB47BC', '#7E57C2', '#5C6BC0', '#42a5f5', '#29b6f6', '#26c6da', 
                   '#26a69a', '#66bb6a', '#9ccc65', '#9C27B0', '#673AB7', '#3F51B5', 
                   '#2196f3', '#03a9f4', '#00bcd4', '#009688', '#4caf50', '#8bc34a',
                   '#8E24AA', '#5E35B1', '#3949AB', '#1e88e5', '#039be5', '#00acc1', 
                   '#00897b', '#43ad47', '#7cb342']

days_to_int = {'Monday':0, 'Tuesday':1, 'Wednesday':2, 'Thursday':3, 'Friday':4, 'Saturday':5, 'Sunday':6}

def find_days_left(base_chore, userchores, days_left):
    """Take a chore and find all unclaimed occurances"""
    for chore in userchores:
        if chore.commitment == 'INIT':
            pass
        elif chore.commitment:
            chore.commitment = str(chore.commitment)
            days_committed = chore.commitment.split("|")
            for day in days_committed:
                if day in days_left:
                    days_left.remove(day)
    return days_left



def total_household_labor():
    """Get the total number of minutes for all the chores associated with a user's address"""
    user_id = session["user_id"]
    user = User.query.filter_by(email=user_id).first()
    userchores = Userchore.query.filter_by(address_id=user.address, commitment='INIT').all()
    chore_ids = [userchore.chore_id for userchore in userchores]
    total_labor_minutes = 0
    for item in chore_ids:
        chore = Chore.query.filter_by(chore_id=item)
        print chore, "<---CHORE"
        total_labor_chore = chore.monthly_labor_hours()
        print total_labor_chore, "<---TOTAL LABOR CHORE"
        total_labor_minutes = total_labor_minutes + total_labor_chore
    return total_labor_minutes


def color_picker(n_users):
    """Returns a list of colors equal in length to the number of users from a 
    curated list equal to the number of users"""
    if n_users > len(MY_COLOR_FAMILY):
        print "You have exceeded the mav number of users! Extended capacity coming soon!"
    steps = len(MY_COLOR_FAMILY) / n_users
    user_colors = MY_COLOR_FAMILY[::steps]
    user_colors = user_colors[:n_users]
    return user_colors


def chores_by_date(user_id):
    """Generates a dictionary of one user's chores for a month, grouped by day"""
    #return all chores for this user
    userchores = Userchore.query.filter(Userchore.user_id==user_id, Userchore.commitment!='INIT').all()
    for userchore in userchores:
        userchore.commitment = userchore.commitment.split("|")
    now = datetime.utcnow()
    until = now + timedelta(weeks=4)
    chores_by_date = {}
    for userchore in userchores:
        chore = Chore.query.filter_by(chore_id=userchore.chore_id).first()
        if chore.occurance == 'weekly' or chore.occurance == 'daily':
            weekdays = userchore.commitment
            weekdays = [str(weekday) for weekday in weekdays]
            weekdays = [days_to_int[weekday] for weekday in weekdays if weekday]
            instances = rrule(WEEKLY,dtstart=now,byweekday=weekdays,until=until)
            for instance in instances:
                instance = instance.strftime("%A, %B %d, %Y")
                chores_by_date[instance] = chores_by_date.get(instance, [])
                chores_by_date[instance].append(chore)
        elif chore.occurance == 'monthly':
            monthday = int(chore.date_monthly)
            instances = rrule(MONTHLY,dtstart=now,bymonthday=monthday,until=until)
            for instance in instances:
                instance = instance.strftime("%A, %B %d, %Y")
                chores_by_date[instance] = chores_by_date.get(instance, [])
                chores_by_date[instance].append(chore)

    return chores_by_date


def validate_address(user_details):
    """Send address details to google for validation and standardization"""
    address = "+".join([user_details["address"], user_details["city"], user_details["state"], user_details["zipcode"]])
    address = address.replace(" ", "+")
    geocode_block = address +"+"+ user_details["city"] +"+"+ user_details["state"] +"+"+ user_details["zipcode"]
    google_key = os.environ['GOOGLE_MAPS_GEOCODING']

    payload = {'address': geocode_block, 'key': os.environ['GOOGLE_MAPS_GEOCODING']}
    #Make google give me a JSON object
    r = requests.get(
    "https://maps.googleapis.com/maps/api/geocode/json?", params=payload)
    address_json = r.json()
    #parse JSON for latitutde and longitude
    #requests' immutable dict object is going to be a pain in the next step. Cast as a python dictionary to head this off here.
    update_details = {}
    update_details["latitude"] = address_json[u'results'][0][u'geometry'][u'location'][u'lat']
    update_details["longitude"] = address_json[u'results'][0][u'geometry'][u'location'][u'lng']
    update_details["address"] = address_json[u'results'][0][u'formatted_address']
    update_details["address_street_num"] = (address_json[u'results'][0][u'address_components'][0][u'long_name'])
    update_details["address_street"] = (address_json[u'results'][0][u'address_components'][1][u'long_name'])
    update_details["city"] = (address_json[u'results'][0][u'address_components'][3][u'long_name'])
    update_details["state"] = (address_json[u'results'][0][u'address_components'][5][u'short_name'])
    update_details["zipcode"] = (address_json[u'results'][0][u'address_components'][7][u'long_name'])
    update_details["phone_number"] = user_details["phone_number"]
    update_details["user_avatar"] = user_details["user_avatar"]
    
    return update_details


# Should be obsolete w/ new auth
# def validate_google_token(token):
#     """Validate google OAuth token"""
#     payload = {'token':token}
#     r = requests.get(
#     "https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=" + payload["token"])
#     user_g_profile = r.json()

#     return user_g_profile


def genkey(n):
    """Generate a pseudorandom n-digit key"""
    randkey=""
    seedstring="01234567890!@#$%^&*()_+~{}|:<>?QWERTYUIOPASDFGHJKLZXCVNBM<>qwertyuiopasdfhgjklzxcvbnm"
    for i in range(n):
        rando = random.choice(seedstring)
        randkey = randkey+rando
    return randkey


# def get_current_user():
#     """Get currently logged in user from DB if any"""
#     user_id = session["user_id"]
#     user = User.query.filter_by(email=user_id).first()
#     return user


def total_houehold_labor(user):
    """Get the total number of minutes for all the chores associated with a user's address"""
    userchores = Userchore.query.filter_by(address_id=user.address, commitment='INIT').all()
    chore_ids = [userchore.chore_id for userchore in userchores]
    total_labor_minutes = 0
    for item in chore_ids:
        chore = Chore.query.filter_by(chore_id=item).first()
        total_labor_chore = chore.monthly_labor_hours()
        total_labor_minutes = total_labor_minutes + int(total_labor_chore)

    return total_labor_minutes


def individual_labor(user_id):
    """"Given a user, return how many minutes of monthly labor they've comimtted to"""
    userchores = Userchore.query.filter(Userchore.user_id==user_id, Userchore.commitment!='INIT').all()
    userchores_household = [entry for entry in userchores if entry.commitment!='INIT']
    individual_labor = 0
    for userchore in userchores:
        #userchore.commitment will give us how often a person says they'll do it, string
        chore = Chore.query.filter_by(chore_id=userchore.chore_id).first()
        if chore.occurance == 'monthly':
            individual_labor += chore.duration_minutes
        else:
            times_done = userchore.commitment.split("|")
            individual_labor += int(chore.duration_minutes) * 4 * len(times_done)
    return individual_labor


def newaddress(update_details):
    """Validate a user's address info, create new entry or associate their 
    useraccount with an existing entry"""
    apartment_vert =  update_details.get("apartment", False)
    if apartment_vert:
        address = Address.query.filter_by(standard_address=update_details["address"], 
                                          apartment=apartment_vert).first()
    else:
        address = Address.query.filter_by(standard_address=update_details["address"]).first()
    if address:
        pass
    if not address:
        address =  Address(latitude=update_details["latitude"], 
                           longitude=update_details["longitude"], 
                           standard_address=update_details["address"], 
                           address_street=update_details["address_street"],
                           address_street_num=update_details["address_street_num"],
                           address_city=update_details["city"],
                           address_state=update_details["state"], 
                           address_zip=update_details["zipcode"])
        db.session.add(address)
        db.session.commit()
    if apartment_vert:
        address.apartment=update_details["apartment"]
    user = User.query.filter_by(email=session["user_id"]).first()
    user.address = address.address_id
    user.avatar_src = update_details["user_avatar"]
    user.phone_number = update_details["phone_number"]
    db.session.commit()


def newchore(name, description, duration_minutes, occurance, by_time, 
                  comment, days_weekly, date_monthly):
    """Clean up chore data and send it to PostgreSQL"""
    if by_time:
            by_time = datetime.datetime.strptime(str(by_time), "%H:%M"),
    else:
            by_time = None
    if occurance == 'daily':
        days_weekly = "Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday"
    elif occurance == 'weekly':
        days_weekly = "|".join(days_weekly)
    new_chore =  Chore(name=name, 
                    description=description, 
                    duration_minutes=duration_minutes, 
                    occurance=occurance, 
                    by_time=by_time, 
                    comment=comment, 
                    days_weekly=days_weekly, 
                    date_monthly=date_monthly)
    db.session.add(new_chore)
    db.session.commit()
    user = User.query.filter_by(email=session["user_id"]).first()
    new_userchore = Userchore(user_id=user.user_id, address_id=user.address, 
                    chore_id=new_chore.chore_id, commitment='INIT')

    db.session.add(new_userchore)
    db.session.commit()


def add_commitment(days_aggreed, chore_id):
    """ Take in a list of days the user is committing to, add their commitment 
    to userchores table """
    user_id = session["user_id"]
    user = User.query.filter_by(email=user_id).first()
    new_userchore = Userchore(user_id=user.user_id, address_id=user.address, 
                    chore_id=chore_id, commitment=days_aggreed)
    db.session.add(new_userchore)
    db.session.commit()