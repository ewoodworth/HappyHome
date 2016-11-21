import requests
import os

def validate_address(address, city, state, zipcode, apartment=""):
    #APARTMENT IS ZIPCODE
    address = "+".join([address, city, state, zipcode])
    address = address.replace(" ", "+")
    geocode_block = address +"+"+ city +"+"+ state +"+"+ zipcode
    google_key = os.environ['GOOGLE_MAPS_GEOCODING']

    payload = {'address': geocode_block, 'key': os.environ['GOOGLE_MAPS_GEOCODING']}
    #Make google give me a JSON object
    r = requests.get(
    "https://maps.googleapis.com/maps/api/geocode/json?", params=payload)
    address_json = r.json()
    #parse JSON for latitutde and longitude
    #SECOND SPRINT: GET SMALLER ELEMENTS FOR ADDRESSES
    latitude = address_json[u'results'][0][u'geometry'][u'location'][u'lat']
    longitude = address_json[u'results'][0][u'geometry'][u'location'][u'lng']
    standard_address = address_json[u'results'][0][u'formatted_address']
    address_street_num = (address_json[u'results'][0][u'address_components'][0][u'long_name'])
    address_street = (address_json[u'results'][0][u'address_components'][1][u'long_name'])
    address_city = (address_json[u'results'][0][u'address_components'][3][u'long_name'])
    address_state = (address_json[u'results'][0][u'address_components'][5][u'short_name'])
    address_zip = (address_json[u'results'][0][u'address_components'][7][u'long_name'])
    apartment = apartment

    address_list = [latitude, longitude, standard_address, address_street_num, address_street, address_city, address_state, address_zip, apartment]

    return address_list

def validate_google_token(token):
    """Validate google OAuth token"""
    payload = {'token':token}
    r = requests.get(
    "https://www.googleapis.com/oauth2/v3/tokeninfo?id_token=" + payload["token"])
    user_g_profile = r.json()

    # name = user_g_profile['given_name']
    # lname = user_g_profile['family_name']
    # email = user_g_profile['email']

    return user_g_profile



def genkey(n):
    """Generate a pseudorandom n-digit key"""
    randkey=""
    seedstring="01234567890!@#$%^&*()_+~{}|:<>?QWERTYUIOPASDFGHJKLZXCVNBM<>qwertyuiopasdfhgjklzxcvbnm"
    for i in range(n):
        rando = random.choice(seedstring)
        randkey = randkey+rando
    return randkey