from bot import *
from rapt_wrapper import *

def test_maps_api():
    latitude, longitude = get_coordonates_from_address('Domaine de la laigne, asnière la giraud')

    get_addr_from_coordonates((latitude, longitude))

    # Request directions via public transit
    now = datetime.now()
    directions_result = gmaps.directions('Sydney Town Hall',
                                     'Parramatta, NSW',
                                     mode='transit',
                                     departure_time=now)

def test_citymapper_api():
    departure = get_coordonates_from_address('Ekino, Levallois perret')
    arrival = get_coordonates_from_address('49 avenue de la redoute, Asnieres sur seine')
    send_citymapper_request(departure, arrival)

def test_ratp_api_request_build():
    request = build_schedule_request(code='13', station='liege')
    print(request)

def test_ratp_api():
    print('Get global traffic information')
    result = get_traffic()
    if result.status_code == 200:
        print(json.dumps(result.json()['result'], indent=4, sort_keys=True))
    else:
        print(result.status_code)
    print('-------------')
    print('Get all metros stations')
    result = get_lines(type='metros')
    if result.status_code == 200:
        print(json.dumps(result.json()['result'], indent=4, sort_keys=True))
    else:
        print(result.status_code)
    print('-------------')
    print('Get line 13')
    result = get_stations(type='metros',code='13')
    if result.status_code == 200:
        print(json.dumps(result.json()['result'], indent=4, sort_keys=True))
    else:
        print(result.status_code)
    print('-------------')
    print('Get destinations of line 13')
    result = get_destinations(type='metros',code='13')
    if result.status_code == 200:
        print(json.dumps(result.json()['result'], indent=4, sort_keys=True))
    else:
        print(result.status_code)
    print('-------------')    
    print('Get schedule of stop Liège on line 13')
    result = get_schedule(code='13', station='liege')
    if result.status_code == 200:
        print(json.dumps(result.json()['result'], indent=4, sort_keys=True))
    else:
        print(result.status_code)
    print('-------------')


if __name__ == '__main__':
    #import bot
    #test_maps_api()
    #test_citymapper_api()
    #test_ratp_api_request_build()
    test_ratp_api()
