from flask import session
from model import User, Address, Chore, Userchore

from dateutil.relativedelta import *
from dateutil.rrule import *
from datetime import datetime

MY_COLOR_FAMILY = ["#339980", "#339999", "#338099", "#336699", "#334d99", 
                   "#333399", "#4d3399", "#663399", "#803399", "#993399", 
                   "#993380", "#993366", "#99334d", "#993333", "#994d33", 
                   "#994d34", "#994d35", "#994d36", "#994d37", "#994d38", 
                   "#994d39", "#994d40", "#994d41", "#994d42"]

days_to_int = {'Monday':0, 'Tuesday':1, 'Wednesday':2, 'Thursday':3, 'Friday':4, 'Saturday':5, 'Sunday':6}

def find_days_left(base_chore, userchores, days_left):
    """Take a chore and find all unclaimed occurances"""
    for chore in userchores:
        if chore.commitment == 'INIT':
            pass
        elif chore.commitment:
            chore.commitment = str(chore.commitment)
            days_committed = chore.commitment.split("|")
            print days_committed, "< < < < < DAYS COMMITTED"
            print days_left, " < < < < < < <DAYS LEFT"
            for day in days_committed:
                print day, "< < < < < < THIS IS THE DAY IN LOOP"
                print days_left, " < < < < < < <DAYS LEFT THAT THE DAY IS GETTING TAKEN OFF OF"
                print type(days_left), "TYPE OF DAYS_LEFT"
                days_left.remove(day)
    return days_left



def total_household_labor():
    """Get the total number of minutes for all the chores associated with a user's address"""
    # (total chore labor for all chores)
    # unique userchores in userchore where userchore.address_id=user.address
    # for these chore_ids
    # total monthly labor per chore sum
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
    until = now + relativedelta(months=+1)
    chores_by_date = {}
    for userchore in userchores:
        chore = Chore.query.filter_by(chore_id=userchore.chore_id).first()
        if chore.occurance == 'weekly' or chore.occurance == 'daily':
            weekdays = userchore.commitment
            weekdays = [days_to_int[weekday] for weekday in weekdays]
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