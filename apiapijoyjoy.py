import requests
import os

def validate_address(address, apartment="", city, state, zipcode):
    address = "+".join(address, apartment, city, state, zipcode)
    address = address.replace(" ", "+")
    geocode_block = address +"+"+ city +"+"+ state +"+"+ zipcode
    google_key = os.environ['GOOGLE_MAPS_GEOCODING']

    payload = {'address': geocode_block, key: os.environ['GOOGLE_MAPS_GEOCODING']}
    #Make google give me a JSON object
    r = requests.get(
    "https://maps.googleapis.com/maps/api/geocode/json?", params=payload)
    address_json = r.json()
    #parse JSON for latitutde and longitude
    #SECOND SPRINT: GET SMALLER ELEMENTS FOR ADDRESSES
    latitude = address_json[u'results'][0][u'geometry'][u'location'][u'lat']
    longitude = address_json[u'results'][0][u'geometry'][u'location'][u'lng']
    standard_address = address_json[u'results'][0][u'formatted_address']

    address_list = [latitude, longitude, standard_address, apartment]

    return address_list


def genkey(n):
    """Generate a pseudorandom n-digit key"""
    randkey=""
    seedstring="01234567890!@#$%^&*()_+~{}|:<>?QWERTYUIOPASDFGHJKLZXCVNBM<>qwertyuiopasdfhgjklzxcvbnm"
    for i in range(n):
        rando = random.choice(seedstring)
        randkey = randkey+rando
    return randkey