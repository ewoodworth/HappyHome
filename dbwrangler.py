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


        