import requests
import os

def validate_address(user_details):
    #APARTMENT IS ZIPCODE

    # [('phone_number', u'4155555555'), ('city', u'San Francisco'), ('state', u'CA'), ('apartment', u'101'), ('user_avatar', u'/static/user_img/7.png'), ('address', u'1410 32nd Ave., 101'), ('zipcode', u'94122')])
    address = "+".join([user_details["address"], user_details["city"], user_details["state"], user_details["zipcode"]])
    address = address.replace(" ", "+")
    geocode_block = address +"+"+ user_details["city"] +"+"+ user_details["state"] +"+"+ user_details["zipcode"]
    google_key = os.environ['GOOGLE_MAPS_GEOCODING']

    payload = {'address': geocode_block, 'key': os.environ['GOOGLE_MAPS_GEOCODING']}
    #Make google give me a JSON object
    r = requests.get(
    "https://maps.googleapis.com/maps/api/geocode/json?", params=payload)
    address_json = r.json()
    #parse JSON for latitutde and longitude
    update_details = {}
    update_details["latitude"] = address_json[u'results'][0][u'geometry'][u'location'][u'lat']
    update_details["longitude"] = address_json[u'results'][0][u'geometry'][u'location'][u'lng']
    update_details["address"] = address_json[u'results'][0][u'formatted_address']
    update_details["address_street_num"] = (address_json[u'results'][0][u'address_components'][0][u'long_name'])
    update_details["address_street"] = (address_json[u'results'][0][u'address_components'][1][u'long_name'])
    update_details["city"] = (address_json[u'results'][0][u'address_components'][3][u'long_name'])
    update_details["state"] = (address_json[u'results'][0][u'address_components'][5][u'short_name'])
    update_details["zipcode"] = (address_json[u'results'][0][u'address_components'][7][u'long_name'])
    update_details["phone_number"] = user_details["phone_number"]
    update_details["user_avatar"] = user_details["user_avatar"]
    
    return update_details

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