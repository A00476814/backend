import requests
import re
import logging
from bs4 import BeautifulSoup
from django.http import JsonResponse
from rentscraper.models import WestwoodListings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def extract_number(size_str):
    match = re.search(r'\d+', size_str.replace(',', ''))
    return float(match.group()) if match else None

def extract_price(price_str):
    return float(re.sub(r'[^\d.]', '', price_str))

def extract_size(size_str):
    match = re.search(r'(\d+)', size_str)
    return int(match.group(1)) if match else None

def fetch_details_from_url(url, title, latitude, longitude, full_url, address, property_type):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')

        amenities = {
            'ParkingAvailable': False,
            'Parking': '',
            'GymAvailable': False,
            'HeatIncluded': False,
            'HotWaterIncluded': False
        }

        amenity_groups = soup.find_all('div', class_='amenity-group')
        for group in amenity_groups:
            for amenity_holder in group.find_all('div', class_='amenity-holder'):
                amenity_text = amenity_holder.get_text(strip=True).lower()
                if 'parking' in amenity_text:
                    amenities['ParkingAvailable'] = True
                    amenities['Parking'] = amenity_text
                if 'fitness' in amenity_text:
                    amenities['GymAvailable'] = True

        utilities_section = soup.find('section', class_='widget utilities')
        if utilities_section:
            utilities_list = utilities_section.find_all('div', class_='utility-holder')
            for utility in utilities_list:
                utility_name = utility.find('h3', class_='name').get_text(strip=True).lower()
                if 'heat' in utility_name:
                    amenities['HeatIncluded'] = True
                if 'water' in utility_name:
                    amenities['HotWaterIncluded'] = True

        apartments = []
        suites = soup.find_all('div', class_='suite')
        for suite in suites:
            suite_type = suite.find('div', class_='suite-type').get_text(strip=True)
            baths = suite.find('div', class_='suite-bath').find('span', class_='value').get_text(strip=True)
            price = suite.find('div', class_='suite-rate').get_text(strip=True).replace('/mo', '').strip()
            sqft = suite.find('div', class_='suite-sqft').get_text(strip=True)

            den_included = 'den' in suite_type.lower()
            bedrooms_match = re.search(r'(\d+)', suite_type, re.IGNORECASE)
            bedrooms = bedrooms_match.group(1) if bedrooms_match else suite_type

            apartments.append({
                'bedrooms': bedrooms,
                'baths': baths,
                'price': price,
                'size': f"{sqft} Ft²",
                'DenIncluded': den_included,
                **amenities,
                'latitude': latitude,
                'longitude': longitude,
                'title': title,
                'full_url': full_url,
                'address': address,
                'property_type': property_type
            })

        return apartments

    except requests.RequestException as e:
        logging.error(f"Error fetching details from {url}: {e}")
        return None

def scrape_listings(request):
    WestwoodListings.objects.all().delete()
    logging.info("Cleared all existing data in WestwoodListings table")

    api_url = "https://api.theliftsystem.com/v2/search?locale=en&client_id=1058&auth_token=sswpREkUtyeYjeoahA2i&city_id=709&geocode=&min_bed=-1&max_bed=100&min_bath=0&max_bath=10&min_rate=0&max_rate=3100&min_sqft=0&max_sqft=10000&show_all_properties=true&show_custom_fields=true&show_promotions=true&region=&keyword=false&property_types=apartments%2C+houses&ownership_types=&exclude_ownership_types=&custom_field_key=&custom_field_values=&order=min_rate+ASC&limit=66&neighbourhood=&amenities=&promotions=&city_ids=1170%2C709&pet_friendly=&offset=0&count=false"

    payload = {
        'latitude': '44.64622549214262',
        'longitude': '-63.632897449999994',
        'radius': '7.226933805643282',
        'page': '0',
        'width': '1000'
    }

    response = requests.get(api_url, params=payload)
    if response.status_code == 200:
        data = response.json()

        listings = []
        for item in data:
            availability_status = item.get('availability_status', 0)
            if availability_status != 0:
                permalink = item.get('permalink', '')
                name = item.get('name', '')
                property_type = item.get('property_type', '')

                address_info = item.get('address', {})
                address = address_info.get('address', '')
                city = address_info.get('city', '')
                province_code = address_info.get('province_code', '')
                postal_code = address_info.get('postal_code', '')
                full_address = f"{address}, {city}, {province_code}, {postal_code}"

                latitude = item.get('geocode', {}).get('latitude', '')
                longitude = item.get('geocode', {}).get('longitude', '')

                if name == "The Mills Residences":
                    permalink = "https://www.westwoodgroup.ca/properties/the-mills"

                listings.append({
                    'full_url': permalink,
                    'title': name,
                    'property_type': property_type,
                    'address': full_address,
                    'latitude': latitude,
                    'longitude': longitude,
                    'availability_status': availability_status
                })

        all_details = []
        for listing in listings:
            url = listing['full_url']
            title = listing['title']
            latitude = listing['latitude']
            longitude = listing['longitude']
            full_url = listing['full_url']
            address = listing['address']
            property_type = listing['property_type']

            if url:
                details = fetch_details_from_url(url, title, latitude, longitude, full_url, address, property_type)
                if details:
                    all_details.extend(details)

        if all_details:
            for listing in all_details:
                WestwoodListings.objects.create(
                    bedrooms=listing['bedrooms'],
                    baths=listing['baths'],
                    price=listing['price'],
                    size=listing['size'],
                    den_included=listing['DenIncluded'],
                    parking_available=listing['ParkingAvailable'],
                    parking=listing['Parking'],
                    gym_available=listing['GymAvailable'],
                    heat_included=listing['HeatIncluded'],
                    hot_water_included=listing['HotWaterIncluded'],
                    latitude=listing['latitude'],
                    longitude=listing['longitude'],
                    title=listing['title'],
                    full_url=listing['full_url'],
                    address=listing['address'],
                    property_type=listing['property_type']
                )

            return JsonResponse({'status': 'success', 'message': f'{len(all_details)} properties scraped and updated successfully.'})
    else:
        return JsonResponse({'status': 'error', 'message': f'Error: {response.status_code} - {response.text}'})
