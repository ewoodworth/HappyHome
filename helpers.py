from flask import session
from model import User, Address, Chore, Userchore


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