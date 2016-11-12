from model import Address, User, Chore, Userchore, db
from flask import session
import datetime

def newaddress(address_list):
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