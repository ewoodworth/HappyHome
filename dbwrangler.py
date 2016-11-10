from model import Address, User, Chore, Userchore, db
from flask import session

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

def newchore(chore_list):
    new_chore =  Chore(name=chore_list[0], 
                 description=chore_list[1], 
                 duration_minutes=chore_list[2], 
                 frequency=chore_list[3])
    db.session.add(new_chore)
    db.session.commit()
    user = User.query.filter_by(email=session["user_id"]).first()
    new_userchore = Userchore(user_id=user.user_id, address_id=user.address, 
                    task_id=new_chore.chore_id, commitment='INIT')
    db.session.add(new_userchore)
    db.session.commit()

def add_commitment(days_aggreed, chore_id):
    """ Take in a list of days the user is committing to, add their commitment to userchores table """
    #HOW COMMUNAL IS THIS DATA, WOULD I BENEFIT TO CALL THIS GLOBALLY IN SERVER?
    user_id = session["user_id"]
    user = User.query.filter_by(email=user_id).first()
    new_userchore = Userchore(user_id=user.user_id, address_id=user.address, 
                    task_id=chore_id, commitment=days_aggreed)
    db.session.add(new_userchore)
    db.session.commit()