from flask import session
from model import User, Address, Chore, Userchore

from dateutil import relativedelta
from dateutil import rrule
from datetime import datetime

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
    until = now + relativedelta(months=+1)
    chores_by_date = {}
    for userchore in userchores:
        chore = Chore.query.filter_by(chore_id=userchore.chore_id).first()
        if chore.occurance == 'weekly' or chore.occurance == 'daily':
            weekdays = userchore.commitment
            weekdays = [str(weekday) for weekday in weekdays]
            print weekdays, "< < < < < < < < WEEKDAYS HERE"
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