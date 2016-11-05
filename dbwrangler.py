def newaddress(address_list):
    latitude, longitude, standard_address, apartment = address_list[latitude, longitude, standard_address, apartment]
    address = Address.query.filter_by(standard_address=standard_address, 
              apartment=apartment).first()
    if not address:
        address =  Address(standard_address=standard_address, latitude=latitude, 
                       longitude=longitude, apartment=apartment)
        db.session.add(address)
        db.session.commit()
    user = User.query.filter_by(email=session["user_id"]).first()
    user.address = address.address_id
    db.session.commit()

def newchore(chore_list):
        if everyday:
        frequency = "daily"
    elif dayofweek:
        frequency = dayofweek
    elif date:
        frequency = "monthly "+date
    by_hour = request.form.get("by_hour")
    by_min = request.form.get("by_min")
    ampm = request.form.get("ampm")
    by_time = ""
    #^This may come back to bite me!!!
    #Number these types. Maybe.
    by_time = by_hour + by_min + ampm
    #Sooo... what if I slip a string field in postgres, an integer. Whose typing wins?
    new_chore =  Chore(name=name, 
                 description=description, 
                 duration_minutes=duration_minutes, 
                 frequency=frequency, 
                 by_time = by_time)
    db.session.add(new_chore)
    db.session.commit()
    user = User.query.filter_by(email=session["user_id"]).first()
    new_userchore = Userchore(user_id=user.user_id, address_id=user.address, 
                    task_id=new_chore.chore_id)
    db.session.add(new_userchore)
    db.session.commit()

