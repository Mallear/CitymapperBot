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
COMMAND_LIST = ['set', 'travel', 'print'] # Commands handled by the bot
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

# Destination related informations for timer task
departure_addr = 'Ekino'
arrival_addr = 'Jouy en josas'


########################
#
#   Google Maps related methods
#
########################

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
    
########################
#
#   CityMapper related methods
#
########################

def send_citymapper_request(departure, arrival, time = None):
    response = requests.get(build_citymapper_request(
                            get_coordonates_from_address(departure), 
                            get_coordonates_from_address(arrival),
                            time))
    print(response.status_code)
    print(response.json()['travel_time_minutes'])
    if response.status_code == 200:
        response = "Travel time from " + str(departure) + " to " + str(arrival) +\
                 " estimated to " + str(response.json()['travel_time_minutes']) + " minutes."
    else:
        response = ""
    slack_client.api_call("chat.postMessage", channel='C46UVV43H',
                            text=response, as_user=True)

def build_citymapper_request(departure, arrival, time = None):
    request_url = CM_ENDPOINT+'startcoord='+str(departure[0])+ '%2C' + str(departure[1])
    request_url = request_url + '&endcoord='+str(arrival[0])+ '%2C' + str(arrival[1])
    if time is not None:
        request_url = request_url + '&time=' +str(time)
        request_url = request_url + '&time_type=arrival'
    request_url = request_url + '&key=' + CITYMAPPER_API_KEY
    return request_url

########################
#
#   Slack related methods
#
########################

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

def handle_command(command, channel):
    """
        Receives commands directed at the bot and determines if they
        are valid commands. If so, then acts on the commands. If not,
        returns back what it needs for clarification.
    """

    # Get command args value
    action = command.split(' ')[0]
    # If action handled, do it
    if action in COMMAND_LIST:
        if action == 'set':
            if check_command(command, channel):
                handle_set_command(command, channel)
        elif action == 'travel':
            if check_command(command, channel):
                handle_travel_command(command, channel)
        elif action == 'print':
            handle_print_command(command, channel)
    else:
        print_help(command, channel)

def check_command(command, channel):
    if 'from' in command:
        if 'to' in command:
            return True
    else:
        print_help(command, channel)
        return False

def handle_set_command(command, channel):
    departure_addr = command.split('from')[1].split('to')[0]
    arrival_addr = command.split('to')[1]
    response = 'Departure address set as : ' + departure_addr + \
                ' and arrival address set as : ' + arrival_addr
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)

def handle_travel_command(command, channel):
    departure = command.split('from')[1].split('to')[0]
    arrival = command.split('to')[1]
    send_citymapper_request(departure, arrival)

def handle_print_command(command, channel):
    response = "Current configuration : \n"
    response = response + 'Departure address set as : ' + str(departure_addr) +\
                 '\nArrival address set as : ' + str(arrival_addr)
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)   

def print_help(command, channel):
    response = "Command unknown, please use these: \n" +\
        "*- @<bot> travel from <address> to <address>*\n" +\
        "*- @<bot> set from <address> to <address>*\n"
    slack_client.api_call("chat.postMessage", channel=channel,
                          text=response, as_user=True)   

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
            command, channel = parse_slack_output(slack_client.rtm_read())
            
            now = datetime.now()

            if command and channel:
                handle_command(command, channel)

            if starting_hour <= now.time() <= ending_hour:
                print(str(last_time <= (now - timedelta(seconds=60*1)).time()))

                if last_time <= (now - timedelta(seconds=60*1)).time():
                    print("Launching time : " + str(now.time()))
                    last_time = now.time()
                    send_citymapper_request(departure_addr, arrival_addr)
    else:
        print("Connection failed. Invalid Slack token or bot ID?")
