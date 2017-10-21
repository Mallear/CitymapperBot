import requests

ENDPOINT = 'https://api-ratp.pierre-grimaud.fr/v3'

def format_station_name(station):
    if station != None :
        station.replace(' ','+')
    return station

def build_schedule_request( code, station, type='metros', way='A'):
    url = '{0}/{1}/{2}/{3}/{4}/{5}'.format(ENDPOINT, 'schedules', type, code, format_station_name(station), way)
    return url

def get_schedule(code, station, type='metros', way='A'):
    """
        Get real time information about next time metro
    """
    endpoint = build_schedule_request(code, station, type, way)
    return requests.get(endpoint)

def build_traffic_request(type=None):
    url = '{}/{}'.format(ENDPOINT, 'traffic')
    if type != None:
        url = '{}/{}'.format(url, type)
    return url

def get_traffic(type=None):
    """
        Get traffic information about all metros/rer/bus lines
    """
    endpoint = build_traffic_request(type)
    return requests.get(endpoint)

def build_stations_request(type, code):
    url = '{}/{}/{}/{}'.format(ENDPOINT, 'stations', type, code)
    return url

def get_stations(type,code):
    """
        Get all the stations of a line
    """
    endpoint = build_stations_request(type, code)
    return requests.get(endpoint)

def build_destinations_request(type, code):
    url = '{}/{}/{}/{}'.format(ENDPOINT, 'destinations', type, code)
    return url

def get_destinations(type, code):
    """
        Get both terminus names.
    """
    endpoint = build_destinations_request(type, code)
    return requests.get(endpoint)

def build_lines_request(type=None, code=None):
    url = '{}/{}'.format(ENDPOINT,'lines')
    if type != None:
        url = '{}/{}'.format(url, type)
        if code != None:
            url = '{}/{}'.format(url, code)
    return url

def get_lines(type=None, code=None):
    """
        Get all lines of transport 
    """
    endpoint = build_lines_request(type, code)
    return requests.get(endpoint)