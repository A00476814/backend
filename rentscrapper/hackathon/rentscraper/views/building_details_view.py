import requests
import logging

from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from rentscraper.models import BuildingDetails
import pandas as pd
import math
from shapely.geometry import Point, Polygon

# Set up logging
logger = logging.getLogger(__name__)

def load_csv():
    # Load CSV into a DataFrame (replace 'path_to_csv_file.csv' with the actual path to the CSV file)
    df = pd.read_csv("D:\\halifax_buildings_merged.csv")
    logger.info("CSV loaded successfully with columns: %s", df.columns)
    return df

def call_walkscore_api(address, latitude, longitude):
    api_key = settings.WALK_SCORE_API_KEY
    url = 'https://api.walkscore.com/score'
    params = {
        'format': 'json',
        'address': address,
        'lat': latitude,
        'lon': longitude,
        'transit': 1,
        'bike': 1,
        'wsapikey': api_key
    }
    response = requests.get(url, params=params)
    data = response.json()
    logger.info("Walkscore API response for %s: %s", address, data)

    walk_score = data.get('walkscore', None)
    transit_score = data.get('transit', {}).get('score', None)
    bike_score = data.get('bike', {}).get('score', None)

    return walk_score, transit_score, bike_score

def find_nearest_place(api_key, location, place_type):
    url = 'https://maps.googleapis.com/maps/api/place/nearbysearch/json'
    params = {
        'location': location,
        'rankby': 'distance',
        'type': place_type,
        'key': api_key
    }
    response = requests.get(url, params=params)
    places = response.json().get('results', [])
    logger.info("Google Places API response for %s: %s", place_type, places)

    if places:
        nearest_place = places[0]
        place_name = nearest_place['name']
        place_address = nearest_place['vicinity']
        place_location = nearest_place['geometry']['location']
        return place_name, place_address, place_location
    return None, None, None

def calculate_travel_time(api_key, origin, destination):
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    params = {
        'origins': origin,
        'destinations': destination,
        'key': api_key
    }
    response = requests.get(url, params=params)
    result = response.json().get('rows', [])[0].get('elements', [])[0]
    logger.info("Google Distance Matrix API response for %s to %s: %s", origin, destination, result)

    travel_time = result.get('duration', {}).get('text', None)
    return travel_time

def call_google_api(api_key, latitude, longitude):
    location = f"{latitude},{longitude}"
    place_types = ['police', 'supermarket', 'pharmacy', 'hospital']
    results = {}

    for place_type in place_types:
        place_name, place_address, place_location = find_nearest_place(api_key, location, place_type)
        if place_location:
            destination = f"{place_location['lat']},{place_location['lng']}"
            travel_time = calculate_travel_time(api_key, location, destination)
            results[place_type] = {
                'name': place_name,
                'address': place_address,
                'travel_time': travel_time
            }
    logger.info("Google API results for %s, %s: %s", latitude, longitude, results)
    return results
# Define polygon coordinates for each area
polygons = {
    "SouthEnd": Polygon([
        (-63.6030424, 44.6362854),
        (-63.6000383, 44.6331705),
        (-63.5711992, 44.6172878),
        (-63.5539472, 44.6182042),
        (-63.5620153, 44.6362243),
        (-63.5671651, 44.635125),
        (-63.5730875, 44.6430033),
        (-63.6030424, 44.6362854)
    ]),
    "Central Halifax": Polygon([
        (-63.6020124, 44.6365297),
        (-63.5746324, 44.642759),
        (-63.5790098, 44.6508806),
        (-63.5809839, 44.6504532),
        (-63.5839879, 44.6524071),
        (-63.576349, 44.6562537),
        (-63.5866487, 44.6616872),
        (-63.6026132, 44.6489266),
        (-63.6080205, 44.647339),
        (-63.6020124, 44.6365297)
    ]),
    "Downtown": Polygon([
        (-63.576349, 44.6562537),
        (-63.5839879, 44.6524071),
        (-63.5809839, 44.6504532),
        (-63.5790098, 44.6508806),
        (-63.5746324, 44.642759),
        (-63.5730875, 44.6430033),
        (-63.5671651, 44.635125),
        (-63.5620153, 44.6362243),
        (-63.5679376, 44.6497205),
        (-63.576349, 44.6562537)
    ]),
    "West End": Polygon([
        (-63.6020124, 44.6365297),
        (-63.6080205, 44.647339),
        (-63.6026132, 44.6489266),
        (-63.5987508, 44.6522239),
        (-63.6016691, 44.6537504),
        (-63.6045015, 44.6549104),
        (-63.6088788, 44.65778),
        (-63.6106813, 44.659001),
        (-63.6123121, 44.6599779),
        (-63.6144578, 44.6605273),
        (-63.6166036, 44.6607105),
        (-63.6196935, 44.6603442),
        (-63.6214101, 44.6610157),
        (-63.6231267, 44.6627251),
        (-63.6275041, 44.6624809),
        (-63.6309373, 44.6632745),
        (-63.6280191, 44.6620535),
        (-63.6277616, 44.6610157),
        (-63.6286199, 44.6600389),
        (-63.6301649, 44.6537504),
        (-63.6307657, 44.6501479),
        (-63.630594, 44.6495983),
        (-63.629564, 44.6486824),
        (-63.6294782, 44.6474611),
        (-63.6287916, 44.6461788),
        (-63.6262166, 44.6449575),
        (-63.6214101, 44.6425758),
        (-63.6198652, 44.6413544),
        (-63.6030424, 44.6362854),
        (-63.6020124, 44.6365297)
    ]),
    "North End": Polygon([
        (-63.6309373, 44.6632745),
        (-63.6275041, 44.6624809),
        (-63.6231267, 44.6627251),
        (-63.6214101, 44.6610157),
        (-63.6196935, 44.6603442),
        (-63.6166036, 44.6607105),
        (-63.6144578, 44.6605273),
        (-63.6116741, 44.659821),
        (-63.605666, 44.6556694),
        (-63.6027477, 44.6544483),
        (-63.6001728, 44.6530439),
        (-63.5987508, 44.6522239),
        (-63.5866487, 44.6616872),
        (-63.5873841, 44.6631787),
        (-63.6037777, 44.6755699),
        (-63.6167381, 44.6777061),
        (-63.6275528, 44.6717857),
        (-63.6309373, 44.6632745)
    ]),
    "Clayton Park": Polygon([
        (-63.6305569, 44.6515785),
        (-63.6286199, 44.6600389),
        (-63.6277616, 44.6610157),
        (-63.6280191, 44.6620535),
        (-63.6309373, 44.6632745),
        (-63.6444615, 44.6761803),
        (-63.647723, 44.6753258),
        (-63.6498688, 44.6749596),
        (-63.6498688, 44.673983),
        (-63.6514137, 44.6736168),
        (-63.6523579, 44.6730675),
        (-63.6523579, 44.6720909),
        (-63.6522721, 44.6709922),
        (-63.6531304, 44.6703818),
        (-63.6551045, 44.6695883),
        (-63.6568211, 44.6695272),
        (-63.6598252, 44.6723961),
        (-63.6602543, 44.6716026),
        (-63.6610268, 44.6708701),
        (-63.6624859, 44.6701987),
        (-63.6642025, 44.6703207),
        (-63.6671208, 44.6692831),
        (-63.6701248, 44.6679402),
        (-63.6720131, 44.6658647),
        (-63.6743305, 44.6664751),
        (-63.6768196, 44.6695883),
        (-63.6743305, 44.6585389),
        (-63.6716698, 44.6521281),
        (-63.6692665, 44.6497467),
        (-63.6642025, 44.6460219),
        (-63.6587952, 44.6443731),
        (-63.6535595, 44.6434571),
        (-63.6509846, 44.6437013),
        (-63.6324452, 44.6513954),
        (-63.6305569, 44.6515785)
    ]),
    "Larry Uteck Area": Polygon([
        (-63.6954266, 44.6961964),
        (-63.6864573, 44.6996435),
        (-63.6804062, 44.7001011),
        (-63.670879, 44.7003146),
        (-63.6661583, 44.6972642),
        (-63.6586052, 44.6972947),
        (-63.6582619, 44.7018703),
        (-63.6648279, 44.7012908),
        (-63.669334, 44.7022059),
        (-63.6772305, 44.7026939),
        (-63.6865431, 44.7022974),
        (-63.6905771, 44.7006807),
        (-63.6949974, 44.7003146),
        (-63.6999327, 44.7007722),
        (-63.7042242, 44.704646),
        (-63.7069279, 44.7072386),
        (-63.7092238, 44.71099),
        (-63.7111121, 44.7126369),
        (-63.713687, 44.7118745),
        (-63.7120133, 44.7091906),
        (-63.7071209, 44.703853),
        (-63.702529, 44.6979962),
        (-63.6954266, 44.6961964)
    ]),
    "RockingHam": Polygon([
        (-63.6954266, 44.6961964),
        (-63.6768196, 44.6695883),
        (-63.6743305, 44.6664751),
        (-63.6720131, 44.6658647),
        (-63.6701248, 44.6679402),
        (-63.6642025, 44.6703207),
        (-63.6624859, 44.6701987),
        (-63.6598252, 44.6723961),
        (-63.6568211, 44.6695272),
        (-63.6551045, 44.6695883),
        (-63.6522721, 44.6709922),
        (-63.6523579, 44.6730675),
        (-63.6498688, 44.673983),
        (-63.6498688, 44.6749596),
        (-63.6444615, 44.6761803),
        (-63.6586052, 44.6972947),
        (-63.6661583, 44.6972642),
        (-63.670879, 44.7003146),
        (-63.6864573, 44.6996435),
        (-63.6954266, 44.6961964)
    ]),
    "Bedford": Polygon([
        (-63.6582619, 44.7018703),
        (-63.6459037, 44.7112064),
        (-63.648307, 44.7242582),
        (-63.6422988, 44.7329781),
        (-63.6426422, 44.7402335),
        (-63.648307, 44.7435865),
        (-63.6656448, 44.7426721),
        (-63.6785194, 44.737429),
        (-63.6980888, 44.730722),
        (-63.7098476, 44.7241972),
        (-63.7167141, 44.715842),
        (-63.7111121, 44.7126369),
        (-63.7069279, 44.7072386),
        (-63.6999327, 44.7007722),
        (-63.6905771, 44.7006807),
        (-63.6865431, 44.7022974),
        (-63.6772305, 44.7026939),
        (-63.669334, 44.7022059),
        (-63.6648279, 44.7012908),
        (-63.6582619, 44.7018703)
    ]),
    "DarthMouth": Polygon([
        (-63.6276321, 44.7028606),
        (-63.6138004, 44.6790001),
        (-63.5982654, 44.674667),
        (-63.5830001, 44.663804),
        (-63.5579376, 44.6613621),
        (-63.5466079, 44.6322954),
        (-63.5397415, 44.6037031),
        (-63.5012893, 44.5775422),
        (-63.4394912, 44.5648243),
        (-63.3958892, 44.5924578),
        (-63.3969192, 44.6313182),
        (-63.4755401, 44.6935871),
        (-63.5078124, 44.7175001),
        (-63.5479812, 44.722623),
        (-63.5833435, 44.7231109),
        (-63.6159591, 44.7223791),
        (-63.6276321, 44.7028606)
    ])
}
def calculate_zone(lat, long, address):
    point = Point(long, lat)
    for zone, polygon in polygons.items():
        if polygon.contains(point):
            logger.info("Calculated zone for %s, %s, %s: %s", lat, long, address, zone)
            return zone
    logger.info("Calculated zone for %s, %s, %s: %s", lat, long, address, "Unknown")
    return "Unknown"

def scrape_building_details(request):
    logger.info("Starting to scrape building details")
    # Load CSV data into DataFrame
    df = load_csv()

    for index, row in df.iterrows():
        # Check if building already exists in the database
        if not BuildingDetails.objects.filter(name=row.get('name'), address=row.get('address')).exists():
            logger.info("Processing building: %s, %s", row.get('name'), row.get('address'))

            # Call Walkscore API
            walk_score, transit_score, bike_score = call_walkscore_api(
                row.get('address'), row.get('latitude'), row.get('longitude')
            )

            # Call Google API
            google_api_results = call_google_api(
                settings.GOOGLE_MAPS_API_KEY, row.get('latitude'), row.get('longitude')
            )

            nearest_police_station = google_api_results.get('police', {})
            nearest_superstore = google_api_results.get('supermarket', {})
            nearest_pharmacy = google_api_results.get('pharmacy', {})
            nearest_hospital = google_api_results.get('hospital', {})

            nearest_police_station_str = f"{nearest_police_station.get('name', '')}, {nearest_police_station.get('address', '')}"
            nearest_superstore_str = f"{nearest_superstore.get('name', '')}, {nearest_superstore.get('address', '')}"
            nearest_pharmacy_str = f"{nearest_pharmacy.get('name', '')}, {nearest_pharmacy.get('address', '')}"
            nearest_hospital_str = f"{nearest_hospital.get('name', '')}, {nearest_hospital.get('address', '')}"

            time_to_nearest_hospital = nearest_hospital.get('travel_time', None)
            time_to_nearest_police_station = nearest_police_station.get('travel_time', None)
            time_to_nearest_superstore = nearest_superstore.get('travel_time', None)
            time_to_nearest_pharmacy = nearest_pharmacy.get('travel_time', None)

            # Calculate the zone
            zone = calculate_zone(row.get('latitude'), row.get('longitude'), row.get('address'))

            # Handle missing values
            def get_value(column_name, default_value):
                value = row.get(column_name, default_value)
                if pd.isna(value):
                    return default_value
                return value

            # Create a new BuildingDetails instance
            building = BuildingDetails(
                name=row.get('name'),
                builder_name=row.get('Builder Name'),
                status=row.get('Status'),
                address=row.get('address'),
                latitude=get_value('latitude', 0.0),
                longitude=get_value('longitude', 0.0),
                zone=zone,
                number_of_floors=get_value('number_of_floors', 0),
                property_type=row.get('property_type', ''),
                number_of_units=get_value('number_of_units', 0),
                year_built=get_value('year_built', 0),
                air_conditioning=row.get('Air Conditioning', False),
                balcony_patio=row.get('Balcony/Patio', False),
                convenience_store=row.get('Convenience Store', False),
                elevator=row.get('Elevator', False),
                fitness_center=row.get('Fitness Center', False),
                free_outdoor_parking=row.get('Free outdoor parking', False),
                heat_included=row.get('Heat Included', False),
                laundry_facilities=row.get('Laundry facilities', False),
                water_included=row.get('Water Included', False),
                parking_available=row.get('parking_available', False),
                parking_cost=get_value('parking_cost', 0),
                parking_type=row.get('parking_type', ''),
                walk_score=walk_score,
                transit_score=transit_score,
                bike_score=bike_score,
                nearest_police_station=nearest_police_station_str,
                nearest_superstore=nearest_superstore_str,
                nearest_pharmacy=nearest_pharmacy_str,
                nearest_hospital=nearest_hospital_str,
                time_to_nearest_hospital=time_to_nearest_hospital,
                time_to_nearest_police_station=time_to_nearest_police_station,
                time_to_nearest_superstore=time_to_nearest_superstore,
                time_to_nearest_pharmacy=time_to_nearest_pharmacy,
            )

            # Save the instance to the database
            building.save()
            logger.info("Saved building details: %s", building)

    return JsonResponse({'message': 'CSV data processed and data saved to the database'})
