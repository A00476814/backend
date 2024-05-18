import requests
import re
import numpy as np
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from django.http import JsonResponse
from rentscraper.models import TempletonListing

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_number(size_str):
    match = re.search(r'\d+', size_str.replace(',', ''))
    return float(match.group()) if match else None

def fetch_listings():
    url = "https://api.theliftsystem.com/v2/search"
    headers = {
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Accept-Language": "en-CA,en-US;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
        "Origin": "https://www.templetonproperties.ca",
        "Referer": "https://www.templetonproperties.ca/",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "cross-site",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36 Edg/123.0.0.0",
    }
    params = {
        "locale": "en",
        "only_available_suites": "",
        "show_all_properties": "",
        "client_id": "584",
        "auth_token": "sswpREkUtyeYjeoahA2i",
        "city_ids": "1170",
        "geocode": "",
        "min_bed": "-1",
        "max_bed": "5",
        "min_bath": "-1",
        "max_bath": "10",
        "min_rate": "0",
        "max_rate": "10000",
        "property_types": "apartments,houses",
        "order": "min_rate ASC, max_rate ASC, min_bed ASC, max_bed ASC",
        "limit": "9999",
        "offset": "0",
        "count": "false",
        "show_custom_fields": "true",
        "show_amenities": "true",
    }

    logging.info("Fetching listings from the API")
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        logging.info("Successfully fetched listings")
        return response.json()
    else:
        logging.error("Failed to retrieve data from the API")
        return []

def fetch_details_from_url(url, title, latitude, longitude, full_url, address, property_type, size_min, size_max, size_avg):
    try:
        logging.info(f"Fetching details for property: {title} ({full_url})")
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        def extract_amenities():
            amenity_groups = soup.find_all('div', class_='amenity-group')
            amenities = {
                'Suite Amenities': [],
                'Building Amenities': [],
                'utilities': [],
                'Parking': [],
                'Pet Policy': []
            }

            for group in amenity_groups:
                group_title = group.find('h2').get_text(strip=True)
                if 'suite' in group_title.lower():
                    key = 'Suite Amenities'
                elif 'building' in group_title.lower():
                    key = 'Building Amenities'
                elif 'utilities' in group_title.lower():
                    key = 'utilities'
                elif 'parking' in group_title.lower():
                    key = 'Parking'
                elif 'pet policy' in group_title.lower():
                    key = 'Pet Policy'
                else:
                    continue

                for amenity in group.find_all('div', class_='amenity-holder'):
                    amenities[key].append(amenity.get_text(strip=True))

            for key, value in amenities.items():
                amenities[key] = ', '.join(value)

            return amenities

        amenities = extract_amenities()

        def extract_utilities():
            utilities_list = []
            utilities_section = soup.find('section', class_='widget utilities')
            if utilities_section:
                utility_holders = utilities_section.find_all('div', class_='utility-holder')
                for utility in utility_holders:
                    name = utility.find('span', class_='name').get_text(strip=True) if utility.find('span', 'name') else ''
                    included = utility.find('span', 'included').get_text(strip=True) if utility.find('span', 'included') else ''
                    utilities_list.append(f"{name} {included}")
            return ', '.join(utilities_list)

        amenities['utilities'] = extract_utilities()

        def extract_parking_info():
            parking_header = soup.find('h2', string=lambda text: 'Parking' in text)
            parking_info = ""
            if parking_header:
                parking_tag = parking_header.find_next('p')
                if parking_tag:
                    parking_info = parking_tag.get_text(strip=True)
            return parking_info

        amenities['Parking'] = extract_parking_info()

        def extract_image_urls():
            image_urls = []
            for a_tag in soup.select('a.gallery-image'):
                image_url = a_tag['href']
                image_urls.append(image_url)
            return ';'.join(image_urls)

        image_urls = extract_image_urls()

        utilities_list = amenities['utilities'].lower()
        HeatIncluded = 'heat' in utilities_list
        HotWaterIncluded = 'water' in utilities_list
        HydroIncluded = 'electricity' in utilities_list

        ParkingAvailable = bool(amenities['Parking'])

        pet_policy_list = amenities['Pet Policy'].lower()
        CatAllowed = 'cats' in pet_policy_list
        DogAllowed = 'dogs' in pet_policy_list

        building_amenities_list = amenities['Building Amenities'].lower()
        GymAvailable = 'fitness' in building_amenities_list
        InBuildingLaundry = 'laundry' in building_amenities_list

        apartments = []

        suites_custom_container = soup.find('div', class_='suites-custom')
        if suites_custom_container:
            suite_groups = suites_custom_container.find_all('div', class_='suite-group-suites')
            for suite_group in suite_groups:
                suites = suite_group.find_all('div', class_='suite')
                suite_details_list = []
                for suite in suites:
                    suite_type = suite.find('div', class_='suite-type').get_text(strip=True) if suite.find('div', 'suite-type') else 'N/A'
                    if 'Bachelor' in suite_type:
                        bedrooms = 'Bachelor'
                    else:
                        bedroom_match = re.search(r'(\d+)', suite_type)
                        bedrooms = bedroom_match.group(1) if bedroom_match else suite_type

                    suite_details = {
                        'bedrooms': bedrooms,
                        'baths': suite.find('div', 'suite-bath').get_text(strip=True) if suite.find('div', 'suite-bath') else 'N/A',
                        'price': suite.find('div', 'suite-rate').get_text(strip=True) if suite.find('div', 'suite-rate') else 'N/A',
                        'HeatIncluded': HeatIncluded,
                        'HotWaterIncluded': HotWaterIncluded,
                        'HydroIncluded': HydroIncluded,
                        'ParkingAvailable': ParkingAvailable,
                        'CatAllowed': CatAllowed,
                        'DogAllowed': DogAllowed,
                        'GymAvailable': GymAvailable,
                        'InBuildingLaundry': InBuildingLaundry,
                        'latitude': latitude,
                        'longitude': longitude,
                        'title': title,
                        'full_url': full_url,
                        'address': address,
                        'property_type': property_type,
                        'image_urls': image_urls,
                        'date': datetime.now().date()
                    }
                    suite_details_list.append(suite_details)

                suite_details_list.sort(key=lambda x: (x['bedrooms'], x['baths']))

                size_min_num = extract_number(size_min)
                size_max_num = extract_number(size_max)

                if size_min_num is not None and size_max_num is not None:
                    sizes = np.linspace(size_min_num, size_max_num, len(suite_details_list))
                    for i, suite in enumerate(suite_details_list):
                        suite['size'] = f"{sizes[i]:.0f} Ft²"
                        price_num = extract_number(suite['price'])
                        size_num = sizes[i]
                        if price_num is not None and size_num > 0:
                            suite['price_per_sqft'] = f"{price_num / size_num:.2f}"
                        else:
                            suite['price_per_sqft'] = "N/A"
                else:
                    for suite in suite_details_list:
                        suite['size'] = "N/A"
                        suite['price_per_sqft'] = "N/A"

                apartments.extend(suite_details_list)

        logging.info(f"Completed fetching details for property: {title} ({full_url})")
        return apartments

    except requests.RequestException as e:
        logging.error(f"Error fetching details from {url}: {e}")
        return []

def scrape_and_save_listings(request):
    # Clear all existing data in the TempletonListing table
    TempletonListing.objects.all().delete()
    logging.info("Cleared all existing data in TempletonListing table")

    listings = fetch_listings()
    all_details = []

    for listing in listings:
        address = f"{listing['address']['address']}, {listing['address']['city']}, {listing['address']['province_code']}, {listing['address']['postal_code']}"
        size_min = f"{int(float(listing['statistics']['suites']['square_feet']['min']))} Ft²"
        size_max = f"{int(float(listing['statistics']['suites']['square_feet']['max']))} Ft²"
        size_avg = f"{int(float(listing['statistics']['suites']['square_feet']['average']))} Ft²"
        details = fetch_details_from_url(
            listing['permalink'], listing['name'], listing['geocode']['latitude'], listing['geocode']['longitude'],
            listing['permalink'], address, listing['property_type'], size_min, size_max, size_avg
        )
        if details:
            all_details.extend(details)

    if all_details:
        for detail in all_details:
            listing = TempletonListing(
                bedrooms=detail['bedrooms'],
                baths=detail['baths'],
                price=detail['price'],
                HeatIncluded=detail['HeatIncluded'],
                HotWaterIncluded=detail['HotWaterIncluded'],
                HydroIncluded=detail['HydroIncluded'],
                ParkingAvailable=detail['ParkingAvailable'],
                CatAllowed=detail['CatAllowed'],
                DogAllowed=detail['DogAllowed'],
                GymAvailable=detail['GymAvailable'],
                InBuildingLaundry=detail['InBuildingLaundry'],
                latitude=detail['latitude'],
                longitude=detail['longitude'],
                title=detail['title'],
                full_url=detail['full_url'],
                address=detail['address'],
                property_type=detail['property_type'],
                size=detail['size'],
                price_per_sqft=detail['price_per_sqft'],
                image_urls=detail['image_urls'],
                date=detail['date']
            )
            listing.save()

    return JsonResponse({'status': 'success', 'message': 'Data has been saved to the database'})
