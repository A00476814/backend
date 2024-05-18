import requests
import re
import logging
import datetime
import time
from bs4 import BeautifulSoup
from django.http import JsonResponse, HttpResponseBadRequest
from django.conf import settings
from rentscraper.models import FutureProperties
from django.db import IntegrityError
from shapely.geometry import Point, Polygon
import googlemaps

# Initialize logger
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define your polygons here for zone calculation
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

# Google Maps API key from Django settings
GOOGLE_MAPS_API_KEY = settings.GOOGLE_MAPS_API_KEY
gmaps = googlemaps.Client(key=GOOGLE_MAPS_API_KEY)

one_year_ago = datetime.datetime.now() - datetime.timedelta(days=365)
start_url = 'https://halifaxdevelopments.ca/'

def get_soup(url):
    response = requests.get(url)
    return BeautifulSoup(response.content, 'html.parser')

def remove_ordinal(date_str):
    return re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

def parse_date(date_str):
    try:
        date_str = remove_ordinal(date_str)
        return datetime.datetime.strptime(date_str, '%d %b %Y')
    except ValueError:
        try:
            return datetime.datetime.strptime(date_str, '%d %B %Y')
        except ValueError:
            logging.error(f"Error parsing date for a post: {date_str}")
            return None

def extract_post_details(post):
    try:
        title_tag = post.find('h2', class_='wp-block-post-title')
        title = title_tag.get_text(strip=True) if title_tag else 'No title'

        blog_link = title_tag.find('a')['href'] if title_tag and title_tag.find('a') else "No link"

        date_tag = post.find('div', class_='wp-block-post-date').find('time')
        date_str = date_tag.get_text(strip=True) if date_tag else 'No date'
        post_date = parse_date(date_str)

        if post_date and post_date < one_year_ago:
            return None  # Skip post if it is older than one year

        image_tag = post.find('figure', class_='wp-block-post-featured-image').find('img')
        image_url = image_tag['src'] if image_tag else 'No image'

        excerpt_tag = post.find('div', class_='wp-block-post-excerpt').find('p')
        excerpt = excerpt_tag.get_text(strip=True) if excerpt_tag else 'No excerpt'

        floors, units, cost, property_type, address, builder = extract_details_from_excerpt(excerpt)

        if address == 'No address' or title == 'No title':
            return None  # Skip post if there is no address or title

        return {
            'title': title,
            'date_of_post': date_str,
            'blog_link': blog_link,
            'image_url': image_url,
            'floors': floors,
            'units': units,
            'cost': cost,
            'property_type': property_type,
            'address': address,
            'builder': builder,
        }
    except Exception as e:
        logging.error(f"Error extracting details for a post: {e}")
        return None

def extract_details_from_excerpt(excerpt):
    try:
        floors = re.search(r'(\d+)\s*Floors?', excerpt)
        floors = floors.group(0) if floors else 'No floors'

        units = re.search(r'(\d+)\s*Units?', excerpt)
        units = units.group(0) if units else 'No units'

        cost = re.search(r'\$\d+\.?\d*\s*[MK]?', excerpt)
        cost = cost.group(0) if cost else 'Not Available'

        address_match = re.search(r'\|\s*([^|]*?\s*(Halifax|Bedford|Dartmouth))\b', excerpt)
        address = address_match.group(1).strip() if address_match else 'No address'

        property_type = re.search(r'(\bResidential\b|\bCommercial\b|\bMixed-Use\b)', excerpt)
        property_type = property_type.group(0) if property_type else 'No property type'

        builder_parts = excerpt.split('|')
        builder = builder_parts[-1].strip() if len(builder_parts) > 1 else 'No builder'

        if 'Unknown' in builder:
            builder = 'Unknown'

        return floors, units, cost, property_type, address, builder
    except Exception as e:
        logging.error(f"Error extracting details from excerpt: {e}")
        return 'No floors', 'No units', 'No cost', 'No property type', 'No address', 'No builder'

def calculate_zone(lat, long, address):
    point = Point(long, lat)
    for zone, polygon in polygons.items():
        if polygon.contains(point):
            logging.info(f"Calculated zone for {lat}, {long}, {address}: {zone}")
            return zone
    logging.info(f"Calculated zone for {lat, long, address}: Unknown")
    return "Unknown"

def get_lat_long(address):
    geocode_result = gmaps.geocode(address)
    if geocode_result and len(geocode_result) > 0:
        location = geocode_result[0]['geometry']['location']
        return location['lat'], location['lng']
    return None, None

def scrape_posts(url):
    soup = get_soup(url)
    posts = soup.find_all('li', class_='wp-block-post')
    post_details = [extract_post_details(post) for post in posts]
    return [details for details in post_details if details]

def scrape_all_pages():
    next_page_url = start_url
    all_posts = []

    start_time = time.time()

    while next_page_url:
        logging.info(f"Scraping {next_page_url}")
        posts = scrape_posts(next_page_url)
        if not posts:
            break  # Stop scraping if no more posts are found

        all_posts.extend(posts)

        soup = get_soup(next_page_url)
        next_page_tag = soup.find('a', class_='wp-block-query-pagination-next')
        next_page_url = next_page_tag['href'] if next_page_tag else None

        last_post_date_str = posts[-1]['date_of_post']
        last_post_date = parse_date(last_post_date_str)
        if last_post_date and last_post_date < one_year_ago:
            break

    new_entries = []

    for post in all_posts:
        title = post['title']
        if FutureProperties.objects.filter(title=title).exists():
            logging.info(f"Duplicate entry found, skipping: {title}")
            continue

        address = post['address']
        lat, long = get_lat_long(address)
        if lat and long:
            zone = calculate_zone(lat, long, address)
        else:
            lat, long, zone = None, None, 'Unknown'

        try:
            new_entry = FutureProperties.objects.create(
                title=post['title'],
                date_of_post=post['date_of_post'],
                blog_link=post['blog_link'],
                image_url=post['image_url'],
                floors=post['floors'],
                units=post['units'],
                cost=post['cost'],
                property_type=post['property_type'],
                address=post['address'],
                builder=post['builder'],
                latitude=lat,
                longitude=long,
                zone=zone
            )
            new_entries.append(new_entry)
            logging.info(f"New entry added: {new_entry.title}")
        except IntegrityError as e:
            logging.error(f"Error adding entry to database: {e}")

    end_time = time.time()
    logging.info(f"Total time taken: {end_time - start_time:.2f} seconds")
    return new_entries

def scrape_new_properties(request):
    if request.method == 'GET':
        new_entries = scrape_all_pages()
        return JsonResponse({
            'status': 'success',
            'message': f'{len(new_entries)} new properties scraped and added successfully.',
            'new_entries': [entry.title for entry in new_entries]
        })
    else:
        return HttpResponseBadRequest('Invalid request method.')
