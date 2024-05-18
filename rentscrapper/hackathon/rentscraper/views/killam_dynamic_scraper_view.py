import time
import logging
import pandas as pd
import re
import json
from bs4 import BeautifulSoup
import htmlmin
import openai
from playwright.sync_api import sync_playwright
from django.conf import settings
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from rentscraper.models import RentalListing
from datetime import date

# Set up OpenAI API key
openai.api_key = settings.OPEN_AI_API_KEY

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger()

def get_full_html(url):
    logger.info(f"Fetching HTML content for URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until="networkidle")
        html = page.content()
        browser.close()

    logger.info(f"Completed fetching HTML content for URL: {url}")
    return html

def parse_property_links(content):
    logger.info("Parsing property links")
    soup = BeautifulSoup(content, 'html.parser')
    property_cards = soup.find_all('div', class_='killam-search-result-card')
    logger.info(f"Found {len(property_cards)} property cards")
    return property_cards[:1]  # Process only the first property card

def extract_details_from_html(html):
    minified_html = htmlmin.minify(html)
    prompt = f"Extract the following details from the HTML: \
               a. Apartment Location latitude \
               b. Apartment Location Longitude \
               c. All the image urls \
               d. href which has 'node' in the url \
               e. Title of the property \
               f. Address of the property \n\n\
               your response should be just a json object and no extra text as i want to parse your response Json structure : \n\
               {{\
                 \"latitude\": \"val\",\
                 \"longitude\": \"val\",\
                 \"image_urls\": [\
                   \"val\",\
                   \"val\",\
                   \"val\"\
                 ],\
                 \"node_href\": \"val\",\
                 \"title\": \"val\",\
                 \"address\": \"val\"\
               }} \n\nHTML: {minified_html}"

    logger.info("Extracting details from HTML using GPT-4")
    while True:
        try:
            response = openai.ChatCompletion.create(
                model='gpt-4o',
                messages=[
                    {"role": "system",
                     "content": "You are an assistant that specializes in parsing HTML and extracting structured data."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000
            )
            break
        except openai.error.RateLimitError as e:
            logger.warning(f"Rate limit exceeded. Error message: {e}")
            match = re.search(r'Please try again in (\d+(\.\d+)?)s', str(e))
            if match:
                wait_time = float(match.group(1)) + 5  # Add a buffer of 5 seconds
                logger.info(f"Waiting for {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                logger.warning("Could not parse wait time from error message. Waiting for 60 seconds...")
                time.sleep(60)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None

    logger.info("Completed extracting details from HTML")
    response_content = response.choices[0]['message']['content']

    json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
    if json_match:
        json_str = json_match.group(0)
        return json_str
    else:
        logger.error("Failed to extract JSON object from response")
        return None

def process_main_page(url):
    content = get_full_html(url)
    property_cards = parse_property_links(content)

    property_details = []
    for card in property_cards:
        details = extract_details_from_html(str(card))
        if details:
            property_details.append(details)

    logger.info(f"Processed {len(property_details)} properties for URL: {url}")
    return property_details

def parse_individual_property_details(content):
    logger.info("Parsing individual property details")
    soup = BeautifulSoup(content, 'html.parser')
    main_content = soup.find('div', id='main-content', class_='container l-sidebar-right grid')
    return main_content

def extract_individual_details_from_html(html):
    if not isinstance(html, str):
        html = str(html)
    minified_html = htmlmin.minify(html)
    prompt = (f"This is HTML containing property details. Analyze it to fill up the JSON below and return only the "
              f"JSON in the response. The flags are boolean like heat included. In available properties, only return "
              f"the unique ones without units. The price and size variables are float and make sure to return all the findings in case of lists.\n\nHTML: "
              f"{minified_html}\n\nJSON:\n{{\n  \"HeatIncluded\": \"val\",\n  \"HotWaterIncluded\": \"val\",\n"
              f"\n  \"CatAllowed\": \"val\",\n  \"DogAllowed\": \"val\",\n  \"Balcony\": \"val\",\n  \"InBuildingLaundry\": \"val\","
              f"\n  \"ParkingAvailable\": \"val\",\n  \"GymAvailable\": \"val\",\n  \"AvailableApartments\": [\n    {{\n      \"PricePerMonth\": \"val\",\n      \"Bedrooms\": \"val\",\n      \"Baths\": \"val\",\n      \"Size\": \"val\"\n    }}\n  ],\n  \"BuildingFloorplanPDFLinks\": [\n    {{\n      \"title\": \"val\",\n      \"url\": \"val\"\n    }}\n  ]\n}}")

    logger.info("Extracting individual property details from HTML using GPT-4o")
    while True:
        try:
            response = openai.ChatCompletion.create(
                model='gpt-4o',
                messages=[
                    {"role": "system",
                     "content": "You are an assistant that specializes in parsing HTML and extracting structured data."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000
            )
            response_content = response['choices'][0]['message']['content']

            json_match = re.search(r'\{.*\}', response_content, re.DOTALL)
            if json_match:
                json_str = json_match.group(0)
                return json_str
            else:
                logger.error("Failed to extract JSON object from response")
                return None

        except openai.error.RateLimitError as e:
            logger.warning(f"Rate limit exceeded. Error message: {e}")
            match = re.search(r'Please try again in (\d+(\.\d+)?)s', str(e))
            if match:
                wait_time = float(match.group(1)) + 5  # Add a buffer of 5 seconds
                logger.info(f"Waiting for {wait_time} seconds before retrying...")
                time.sleep(wait_time)
            else:
                logger.warning("Could not parse wait time from error message. Waiting for 60 seconds...")
                time.sleep(60)
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return None

def changeJsonToDataFrame(all_property_details):
    data = []
    base_url = "https://killamreit.com"

    for json_str in all_property_details:
        property_data = json.loads(json_str)

        latitude = property_data.get('latitude', '')
        longitude = property_data.get('longitude', '')
        node_href = base_url + property_data.get('node_href', '')
        title = property_data.get('title', '')
        address = property_data.get('address', '')
        image_urls = property_data.get('image_urls', [])
        concatenated_image_urls = ';'.join(image_urls)

        data.append({
            'latitude': latitude,
            'longitude': longitude,
            'full_url': node_href,
            'title': title,
            'address': address,
            'image_urls': concatenated_image_urls
        })

    df = pd.DataFrame(data)

    return df

def update_property_details(property_listing_df):
    new_rows = []
    for index, row in property_listing_df.iterrows():
        fullHtml = get_full_html(row['full_url'])
        html = parse_individual_property_details(fullHtml)
        details_json_str = extract_individual_details_from_html(html)

        if details_json_str:
            details_json = json.loads(details_json_str)
            available_apartments = details_json.get("AvailableApartments", [])
            building_floorplans = json.dumps(details_json.get("BuildingFloorplanPDFLinks", []))

            for apartment in available_apartments:
                new_row = row.copy()
                new_row['HeatIncluded'] = details_json.get('HeatIncluded', '') == 'true'
                new_row['HotWaterIncluded'] = details_json.get('HotWaterIncluded', '') == 'true'
                new_row['CatAllowed'] = details_json.get('CatAllowed', '') == 'true'
                new_row['DogAllowed'] = details_json.get('DogAllowed', '') == 'true'
                new_row['Balcony'] = details_json.get('Balcony', '') == 'true'
                new_row['InBuildingLaundry'] = details_json.get('InBuildingLaundry', '') == 'true'
                new_row['ParkingAvailable'] = details_json.get('ParkingAvailable', '') == 'true'
                new_row['GymAvailable'] = details_json.get('GymAvailable', '') == 'true'
                new_row['PricePerMonth'] = apartment.get('PricePerMonth', '')
                new_row['Bedrooms'] = apartment.get('Bedrooms', '')
                new_row['Baths'] = apartment.get('Baths', '')
                new_row['Size'] = apartment.get('Size', '')
                new_row['BuildingFloorPlans'] = building_floorplans

                new_rows.append(new_row)

    new_df = pd.DataFrame(new_rows)
    return new_df

def scrape_and_save_rental_listings():
    urls = [
        "https://killamreit.com/apartments?region=Halifax",
        "https://killamreit.com/apartments?region=Dartmouth",
        "https://killamreit.com/apartments?region=Bedford"
    ]

    all_property_details = []
    for url in urls:
        logger.info(f"Processing main page for URL: {url}")
        property_details = process_main_page(url)
        all_property_details.extend(property_details)

    property_listing_df = changeJsonToDataFrame(all_property_details)
    logger.info("Saved main property details to DataFrame")

    final_df = update_property_details(property_listing_df)
    logger.info("Saved individual property details to DataFrame")

    # Clear existing data
    RentalListing.objects.all().delete()
    logger.info("Cleared existing data in RentalListing table")

    # Save new data
    for index, row in final_df.iterrows():
        RentalListing.objects.create(
            latitude=row['latitude'],
            longitude=row['longitude'],
            full_url=row['full_url'],
            title=row['title'],
            address=row['address'],
            image_urls=row['image_urls'],
            price=row['PricePerMonth'],
            bedrooms=row['Bedrooms'],
            baths=row['Baths'],
            size=row['Size'],
            HeatIncluded=row['HeatIncluded'],
            HotWaterIncluded=row['HotWaterIncluded'],
            CatAllowed=row['CatAllowed'],
            DogAllowed=row['DogAllowed'],
            Balcony=row['Balcony'],
            InBuildingLaundry=row['InBuildingLaundry'],
            ParkingAvailable=row['ParkingAvailable'],
            GymAvailable=row['GymAvailable'],
            date=date.today()
        )

    logger.info("Saved all property details to database")

@require_GET
def scrape_rental_listings_view(request):
    scrape_and_save_rental_listings()
    return JsonResponse({'status': 'success', 'message': 'Rental listings scraped and saved successfully.'})
