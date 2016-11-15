from model import Address, User, Chore, Userchore, db
from flask import session
import datetime

def get_current_user():
    """Get currently logged in user from DB if any"""
    user_id = session["user_id"]
    user = User.query.filter_by(email=user_id).first()
    return user

# def total_labor(userchores):
#     """Given a subset of the userchore table, return the total labor minutes for those chores"""

#     return total_labor minutes

def total_houehold_labor(user):
    """Get the total number of minutes for all the chores associated with a user's address"""
    userchores = Userchore.query.filter_by(address_id=user.address, commitment='INIT').all()
    chore_ids = [userchore.chore_id for userchore in userchores]
    total_labor_minutes = 0
    print chore_ids, "<<<<************* < < < <" 
    for item in chore_ids:
        chore = Chore.query.filter_by(chore_id=item).first()
        print chore, "< < < < THIS IS THE CHORE HAPPENING HERE"
        total_labor_chore = chore.monthly_labor_hours()
        total_labor_minutes = total_labor_minutes + int(total_labor_chore)

    return total_labor_minutes

def individual_labor(user_id):
    """"Given a user, return how many minutes of monthly labor they've comimtted to"""
    userchores = Userchore.query.filter(Userchore.user_id==user_id, Userchore.commitment!='INIT').all()
    # print "WE'RE DOING THIS CALCULATION FOR {}".format(user.name)
    # print userchores
    # print len(userchores)
    userchores_household = [entry for entry in userchores if entry.commitment!='INIT']
    # print userchores_household, "USERCHORES"
    individual_labor = 0
    for userchore in userchores:
        #userchore.commitment will give us how often a person says they'll do it, string
        chore = Chore.query.filter_by(chore_id=userchore.chore_id).first() #this chore is what were considdering
        # print chore.name, "THEY'VE AGREED TO DO THIS CHORE"
        if chore.occurance == 'monthly':
            if userchore.commitment:
                individual_labor =+ chore.duration_minutes
                # print individual_labor, "INDIVIDUAL LABOR IN FIRST LOOP"
        else:
            times_done = userchore.commitment.split("|")
            # print chore.duration_minutes, "< < < < < IT TAKES THIS LONG"
            # print times_done, "ITS GETTING MULTIPLIED THIS MUCH"
            individual_labor += int(chore.duration_minutes) * 4 * len(times_done)
            # print individual_labor, "INDIVIDUAL LABOR IN THE SECONFD LOOP>>>> WEEKLY"
    print "INDIVIDUAL LABOR", individual_labor
    return individual_labor

def newaddress(address_list):
    """Validate a user's address info, create new entry or associate their 
    useraccount with an existing entry"""
    latitude, longitude, standard_address, apartment = address_list
    address = Address.query.filter_by(standard_address=standard_address, 
              apartment=apartment).first()
    if address:
        pass
    if not address:
        address =  Address(standard_address=standard_address, latitude=latitude, 
                       longitude=longitude, apartment=apartment)
        db.session.add(address)
        db.session.commit()
    user = User.query.filter_by(email=session["user_id"]).first()
    user.address = address.address_id
    db.session.commit()

def newchore(name, description, duration_minutes, occurance, by_time, 
                  comment, days_weekly, date_monthly):
    """Clean up chore data and send it to PostgreSQL"""
    if by_time:
            by_time = datetime.datetime.strptime(str(by_time), "%H:%M"),
    else:
            by_time = None
    #save day data as pipe-joined string
    if occurance == 'daily':
        days_weekly = "Sunday|Monday|Tuesday|Wednesday|Thursday|Friday|Saturday"
    elif occurance == 'weekly':
        days_weekly = "|".join(days_weekly)
    print days_weekly
    new_chore =  Chore(name=name, 
                    description=description, 
                    duration_minutes=duration_minutes, 
                    occurance=occurance, 
                    by_time=by_time, 
                    commment=comment, 
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
    """ Take in a list of days the user is committing to, add their commitment to userchores table """
    user_id = session["user_id"]
    user = User.query.filter_by(email=user_id).first()
    new_userchore = Userchore(user_id=user.user_id, address_id=user.address, 
                    chore_id=chore_id, commitment=days_aggreed)
    db.session.add(new_userchore)
    db.session.commit()