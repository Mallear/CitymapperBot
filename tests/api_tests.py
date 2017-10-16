from bot import *

def test_maps_api():
    latitude, longitude = get_coordonates_from_address('Domaine de la laigne, asnière la giraud')

    get_addr_from_coordonates((latitude, longitude))

    # Request directions via public transit
    now = datetime.now()
    directions_result = gmaps.directions("Sydney Town Hall",
                                     "Parramatta, NSW",
                                     mode="transit",
                                     departure_time=now)

def test_citymapper_api():
    departure = get_coordonates_from_address('Ekino, Levallois perret')
    arrival = get_coordonates_from_address('49 avenue de la redoute, Asnieres sur seine')
    send_citymapper_request(departure, arrival)

if __name__ == "__main__":
    import bot
    test_maps_api()
    test_citymapper_api()
