import os
import time
import json
import yaml
import requests
from datetime import datetime, time as dtime, timedelta
import googlemaps
from slackclient import SlackClient


# API key loading from config file
with open(os.path.dirname(os.path.abspath(__file__))+'/config.yml', 'r') as file:
    conf = yaml.load(file)
    GOOGLE_API_KEY = conf['googlemaps_api_key']
    SLACK_BOT_TOKEN = conf['slack_bot_token'] 
    CITYMAPPER_API_KEY = conf['citymapper_api_key']


# Slack related informations 
BOT_NAME = 'ekinobot'
COMMAND_LIST = [''] # Commands handled by the bot
slack_client = SlackClient(SLACK_BOT_TOKEN) # instantiate Slack & Twilio clients
channel = "C46UVV43H" # TODO: get channel ID from API

# Google related informations
gmaps = googlemaps.Client(key=GOOGLE_API_KEY) # Instantiate gmaps

# City mapper API related informations
CM_ENDPOINT = "https://developer.citymapper.com/api/1/traveltime/?"
requests_headers = {
            'user-agent': 'curl/7.47.0',
            'Content-Type': 'application/json'
            }


# Timer related information
starting_hour = dtime(6,0)
ending_hour = dtime(6,25)


def get_bot_id():
    api_call = slack_client.api_call("users.list")
    if api_call.get('ok'):
        # retrieve all users so we can find our bot
        users = api_call.get('members')
        for user in users:
            if 'name' in user and user.get('name') == BOT_NAME:
                print(user.get('id')) # Log..ish
                return user.get('id')
    else:
        return None


def parse_slack_output(slack_rtm_output):
    """
        The Slack Real Time Messaging API is an events firehose.
        this parsing function returns None unless a message is
        directed at the Bot, based on its ID.
    """
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None


def is_number(s):
    """
        Homemade check for char as int.
    """
    try:
        int(s)
        return True
    except ValueError:
        return False


def send_travel_time():
    response = "Send travel time : " + str(datetime.now().time()) + " to channel : " + str(channel)
    slack_client.api_call("chat.postMessage", channel='C46UVV43H',
                            text=response, as_user=True)


def get_travel_time():
    pass

def test_maps_api():
    latitude, longitude = get_coordonates_from_address('Domaine de la laigne, asnière la giraud')

    get_addr_from_coordonates((latitude, longitude))

    # Request directions via public transit
    now = datetime.now()
    directions_result = gmaps.directions("Sydney Town Hall",
                                     "Parramatta, NSW",
                                     mode="transit",
                                     departure_time=now)

def get_addr_from_coordonates(coordinates):
    '''
        Coordonates are a pair of (latitude, longitude)
        Return the formatted address
    '''
    reverse_geocode_result = gmaps.reverse_geocode(coordinates)
    print(reverse_geocode_result[0]['formatted_address'])

    return reverse_geocode_result[0]['formatted_address']


def get_coordonates_from_address(addr):
    '''
        addr : formatted adress
        Return pair (latitude, longitude)
    '''
    geocode_result = gmaps.geocode(addr)

    print(geocode_result[0]['geometry']['location'])
    coordinates = geocode_result[0]['geometry']['location']
    return coordinates['lat'], coordinates['lng']
    
def test_citymapper_api():
    departure = get_coordonates_from_address('Ekino, Levallois perret')
    arrival = get_coordonates_from_address('49 avenue de la redoute, Asnieres sur seine')
    send_citymapper_request(departure, arrival)

def send_citymapper_request(departure, arrival, time = None):
    response = requests.get(build_citymapper_request(departure, arrival, time))
    #rint(response.status_code)
    print(response.json())

def build_citymapper_request(departure, arrival, time = None):
    request_url = CM_ENDPOINT+'startcoord='+str(departure[0])+ '%2C' + str(departure[1])
    request_url = request_url + '&endcoord='+str(arrival[0])+ '%2C' + str(arrival[1])
    if time is not None:
        request_url = request_url + '&time=' +str(time)
        request_url = request_url + '&time_type=arrival'
    request_url = request_url + '&key=' + CITYMAPPER_API_KEY
    return request_url

if __name__ == "__main__":
    READ_WEBSOCKET_DELAY = 1 # 1 second delay between reading from firehose
    # starterbot's ID 
    BOT_ID = get_bot_id()
    # constants
    AT_BOT = "<@" + BOT_ID + ">"
    # Get now datetime
    now = datetime.now()
    last_time = now.time()

    if slack_client.rtm_connect():
        print("StarterBot connected and running!")
        while True:
            #command, channel = parse_slack_output(slack_client.rtm_read())
            
            now = datetime.now()
            #print( "Current : " + str(now.time()) + " ; Last : " + str(last_time))
            #print( "Starting : " + str(starting_hour) + " ; Ending : " +str(ending_hour))
            #print(str(starting_hour <= now.time() <= ending_hour))
            #test_maps_api()
            test_citymapper_api()
            if starting_hour <= now.time() <= ending_hour:
                print(str(last_time <= (now - timedelta(seconds=60*1)).time()))

                if last_time <= (now - timedelta(seconds=60*1)).time():
                    print("Launching time : " + str(now.time()))
                    last_time = now.time()
                    send_travel_time()
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
