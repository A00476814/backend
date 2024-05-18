from django.http import JsonResponse
import asyncio
import logging
from urllib.parse import urljoin
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
from datetime import date
from rentscraper.models import RentalListing  # Import the RentalListing model

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

# Base URL for constructing full URLs
BASE_URL = "https://killamreit.com"

async def get_full_html(playwright, url):
    logger.info(f"Fetching HTML content for URL: {url}")
    browser = await playwright.chromium.launch(headless=True)
    page = await browser.new_page()
    await page.goto(url, wait_until='networkidle')
    html = await page.content()
    await browser.close()
    logger.info(f"Completed fetching HTML content for URL: {url}")
    return html

def parse_property_cards(content):
    logger.info("Parsing property cards")
    soup = BeautifulSoup(content, 'html.parser')
    property_cards = soup.find_all('div', class_='killam-search-result-card')
    logger.info(f"Found {len(property_cards)} property cards")
    return property_cards

def extract_property_details(card):
    details = {}
    location_span = card.find('span', class_='apartment-location')
    if location_span:
        details['latitude'] = location_span.get('data-lat', '')
        details['longitude'] = location_span.get('data-lng', '')

    node_links = card.find_all('a', href=True)
    full_url = "URL not found"
    for link in node_links:
        if "node" in link['href']:
            full_url = urljoin(BASE_URL, link['href'])
            break
    if full_url == "URL not found":
        logger.warning(f"Skipped property due to missing node href: {card}")
        return None
    details['full_url'] = full_url

    title_div = card.find('div', class_='killam-search-result-info-title')
    if title_div:
        details['title'] = title_div.text.strip()

    address_div = card.find('div', class_='killam-search-result-info-address')
    if address_div:
        details['address'] = address_div.text.strip()

    image_urls = []
    for img in card.select('.killam-search-result-image img'):
        if img.has_attr('src'):
            image_urls.append(img['src'])
    details['image_urls'] = ';'.join(image_urls)

    return details

def parse_main_content(main_content):
    apartments = []
    amenities = {
        'HeatIncluded': False,
        'HotWaterIncluded': False,
        'CatAllowed': False,
        'DogAllowed': False,
        'Balcony': False,
        'InBuildingLaundry': False,
        'ParkingAvailable': False,
        'GymAvailable': False
    }

    apartments_container = main_content.find('div', id='block-views-block-units-all-units')
    if apartments_container:
        view_content = apartments_container.find('div', class_='view-content')
        if view_content:
            apartment_rows = view_content.find_all('div', class_='views-row')
            seen_apartments = set()

            for row in apartment_rows:
                fields = row.find_all('div', class_='c-unit-row__field')
                apartment_details = {}
                for field in fields:
                    header = field.find('div', class_='c-unit-row__field_header').text.strip()
                    content = field.find('div', class_='c-unit-row__field_content').text.strip()
                    if header == 'Price From (mthly)':
                        apartment_details['price'] = content
                    elif header == 'Bedrooms':
                        apartment_details['bedrooms'] = content
                    elif header == 'Bath':
                        apartment_details['baths'] = content
                    elif header == 'Size (aprox.)':
                        apartment_details['size'] = content
                    elif header == 'Availability':
                        apartment_details['availability'] = content

                apartment_key = (
                    apartment_details.get('price'), apartment_details.get('bedrooms'), apartment_details.get('baths'),
                    apartment_details.get('size'))

                if apartment_key not in seen_apartments:
                    seen_apartments.add(apartment_key)
                    apartments.append(apartment_details)
                else:
                    logger.warning(f"Skipped duplicate apartment: {apartment_details}")
        else:
            logger.warning("Skipped property due to missing view content")
    else:
        logger.warning("Skipped property due to missing apartments container")

    amenities_block = main_content.find('div', id='block-views-block-amenities-amenities-list')
    if amenities_block:
        amenity_rows = amenities_block.find_all('div', class_='views-row')
        for amenity in amenity_rows:
            title = amenity.find('div', class_='c-amenity-item__desc_title').text.strip()
            if title == 'Heat Included':
                amenities['HeatIncluded'] = True
            elif title == 'Hot Water Included':
                amenities['HotWaterIncluded'] = True
            elif title == 'Cat Friendly':
                amenities['CatAllowed'] = True
            elif title == 'Dog Friendly':
                amenities['DogAllowed'] = True
            elif title == 'Balcony':
                amenities['Balcony'] = True
            elif title == 'Laundry (In Building)':
                amenities['InBuildingLaundry'] = True
            elif title == 'Underground / Parking Garage':
                amenities['ParkingAvailable'] = True
            elif title == 'Fitness Gym':
                amenities['GymAvailable'] = True

    return apartments, amenities

async def extract_further_details(playwright, url):
    logger.info(f"Fetching additional details for URL: {url}")
    try:
        content = await get_full_html(playwright, url)
    except Exception as e:
        logger.error(f"Failed to fetch full HTML content for URL: {url} due to error: {e}")
        return [], {}

    soup = BeautifulSoup(content, 'html.parser')

    main_content = soup.find('div', id='main-content', class_='container l-sidebar-right grid')
    if main_content:
        apartments, amenities = parse_main_content(main_content)
        if apartments:
            logger.info(f"Extracted {len(apartments)} apartments and amenities for URL: {url}")
        else:
            logger.warning(f"No apartments found for URL: {url}")
        return apartments, amenities

    logger.warning(f"No main content found for URL: {url}")
    return [], {}

async def scrape_killamreit():
    urls = [
        "https://killamreit.com/apartments?region=Halifax",
        "https://killamreit.com/apartments?region=Dartmouth",
        "https://killamreit.com/apartments?region=Bedford"
    ]

    all_property_cards = []

    async with async_playwright() as playwright:
        for url in urls:
            logger.info(f"Processing URL: {url}")
            content = await get_full_html(playwright, url)
            property_cards = parse_property_cards(content)
            all_property_cards.extend(property_cards)

        logger.info(f"Total property cards found: {len(all_property_cards)}")

        properties = []
        for card in all_property_cards:
            property_details = extract_property_details(card)
            if property_details:
                properties.append(property_details)
            else:
                logger.warning(f"Skipped property card due to missing details: {card}")

        logger.info(f"Total properties with details extracted: {len(properties)}")

        final_details = []

        for property in properties:
            logger.info(f"Processing property: {property['title']} at {property['address']}")
            apartments, amenities = await extract_further_details(playwright, property['full_url'])
            if apartments:
                for apartment in apartments:
                    combined_details = {**property, **apartment, **amenities}
                    final_details.append(combined_details)
            else:
                logger.warning(f"No apartments found for property: {property['title']} at {property['address']}")

        logger.info(f"Total final details: {len(final_details)}")

        return final_details

def scrape_killamreit_view(request):
    # Clear all existing data in the database
    RentalListing.objects.all().delete()
    logger.info("Cleared all existing data in RentalListing table")

    final_details = asyncio.run(scrape_killamreit())

    # Save final details to the database
    for details in final_details:
        RentalListing.objects.create(
            latitude=details.get('latitude', None),
            longitude=details.get('longitude', None),
            full_url=details.get('full_url', ''),
            title=details.get('title', ''),
            address=details.get('address', ''),
            image_urls=details.get('image_urls', ''),
            price=details.get('price', ''),
            bedrooms=details.get('bedrooms', 0),
            baths=details.get('baths', 0),
            size=details.get('size', ''),
            HeatIncluded=details.get('HeatIncluded', False),
            HotWaterIncluded=details.get('HotWaterIncluded', False),
            CatAllowed=details.get('CatAllowed', False),
            DogAllowed=details.get('DogAllowed', False),
            Balcony=details.get('Balcony', False),
            InBuildingLaundry=details.get('InBuildingLaundry', False),
            ParkingAvailable=details.get('ParkingAvailable', False),
            GymAvailable=details.get('GymAvailable', False),
            date=date.today()
        )

    return JsonResponse({'status': 'success', 'data': final_details}, safe=False)
