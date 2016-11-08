from model import Address, User, Chore, Userchore, db
from flask import session

def newaddress(address_list):
    latitude, longitude, standard_address, apartment = address_list
    address = Address.query.filter_by(standard_address=standard_address, 
              apartment=apartment).first()
    if address:
        print "We're using an old address"
    if not address:
        print "We're making a new address"
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