from django.http import JsonResponse
from datetime import timedelta
from django.utils import timezone
from rentscraper.models import RentalListing, TempletonListing, WestwoodListings, MasterPropertyData, BuildingDetails

def update_master_data(request):
    def get_building_details(name):
        try:
            return BuildingDetails.objects.get(name=name)
        except BuildingDetails.DoesNotExist:
            return None

    def should_update(entry, master_entry):
        date_difference = (entry.date - master_entry.date).days
        if date_difference >= 90:
            return True
        return False

    def process_killam_listings():
        listings = RentalListing.objects.all()
        for listing in listings:
            # Check for existing entries in MasterPropertyData
            master_entry = MasterPropertyData.objects.filter(
                name=listing.title,
                bedrooms=listing.bedrooms,
                baths=listing.baths,
                size=listing.size,
                price_per_month=listing.price,
            ).order_by('-date').first()

            if master_entry:
                if not should_update(listing, master_entry):
                    continue

            # Get building details
            building_details = get_building_details(listing.title)

            # Create new master entry
            MasterPropertyData.objects.create(
                name=listing.title,
                builder_name=building_details.builder_name if building_details else '',
                status=building_details.status if building_details else '',
                address=listing.address,
                latitude=listing.latitude,
                longitude=listing.longitude,
                full_url=listing.full_url,
                image_urls=listing.image_urls,
                heat_included=listing.HeatIncluded,
                hot_water_included=listing.HotWaterIncluded,
                cat_allowed=listing.CatAllowed,
                dog_allowed=listing.DogAllowed,
                balcony=listing.Balcony,
                in_building_laundry=listing.InBuildingLaundry,
                parking_available=listing.ParkingAvailable,
                gym_available=building_details.fitness_center if building_details else False,
                price_per_month=listing.price,
                bedrooms=listing.bedrooms,
                baths=listing.baths,
                size=listing.size,
                building_floor_plans='',
                hydro_included=False,  # Not available in Killam data
                property_type=building_details.property_type if building_details else '',
                price_per_sqft='',
                listing_address=listing.address,
                den_included=False,  # Not available in Killam data
                parking='',
                number_of_floors=building_details.number_of_floors if building_details else 0,
                number_of_units=building_details.number_of_units if building_details else 0,
                year_built=building_details.year_built if building_details else 0,
                air_conditioning=building_details.air_conditioning if building_details else False,
                balcony_patio=building_details.balcony_patio if building_details else False,
                convenience_store=building_details.convenience_store if building_details else False,
                elevator=building_details.elevator if building_details else False,
                free_outdoor_parking=building_details.free_outdoor_parking if building_details else False,
                laundry_facilities=building_details.laundry_facilities if building_details else False,
                water_included=building_details.water_included if building_details else False,
                parking_cost=building_details.parking_cost if building_details else 0,
                parking_type=building_details.parking_type if building_details else '',
                walk_score=building_details.walk_score if building_details else 0,
                transit_score=building_details.transit_score if building_details else 0,
                bike_score=building_details.bike_score if building_details else 0,
                nearest_police_station=building_details.nearest_police_station if building_details else '',
                nearest_superstore=building_details.nearest_superstore if building_details else '',
                nearest_pharmacy=building_details.nearest_pharmacy if building_details else '',
                nearest_hospital=building_details.nearest_hospital if building_details else '',
                time_to_nearest_hospital=building_details.time_to_nearest_hospital if building_details else '',
                time_to_nearest_police_station=building_details.time_to_nearest_police_station if building_details else '',
                time_to_nearest_superstore=building_details.time_to_nearest_superstore if building_details else '',
                time_to_nearest_pharmacy=building_details.time_to_nearest_pharmacy if building_details else '',
                zone=building_details.zone if building_details else '',
                date=listing.date,
            )

    def process_templeton_listings():
        listings = TempletonListing.objects.all()
        for listing in listings:
            # Check for existing entries in MasterPropertyData
            master_entry = MasterPropertyData.objects.filter(
                name=listing.title,
                bedrooms=listing.bedrooms,
                baths=listing.baths,
                size=listing.size,
                price_per_month=listing.price,
            ).order_by('-date').first()

            if master_entry:
                if not should_update(listing, master_entry):
                    continue

            # Get building details
            building_details = get_building_details(listing.title)

            # Create new master entry
            MasterPropertyData.objects.create(
                name=listing.title,
                builder_name=building_details.builder_name if building_details else '',
                status=building_details.status if building_details else '',
                address=listing.address,
                latitude=listing.latitude,
                longitude=listing.longitude,
                full_url=listing.full_url,
                image_urls=listing.image_urls,
                heat_included=listing.HeatIncluded,
                hot_water_included=listing.HotWaterIncluded,
                cat_allowed=listing.CatAllowed,
                dog_allowed=listing.DogAllowed,
                balcony=False,  # Not available in Templeton data
                in_building_laundry=listing.InBuildingLaundry,
                parking_available=listing.ParkingAvailable,
                gym_available=building_details.fitness_center if building_details else False,
                price_per_month=listing.price,
                bedrooms=listing.bedrooms,
                baths=listing.baths,
                size=listing.size,
                building_floor_plans='',
                hydro_included=listing.HydroIncluded,
                property_type=listing.property_type,
                price_per_sqft=listing.price_per_sqft,
                listing_address=listing.address,
                den_included=False,  # Not available in Templeton data
                parking='',
                number_of_floors=building_details.number_of_floors if building_details else 0,
                number_of_units=building_details.number_of_units if building_details else 0,
                year_built=building_details.year_built if building_details else 0,
                air_conditioning=building_details.air_conditioning if building_details else False,
                balcony_patio=building_details.balcony_patio if building_details else False,
                convenience_store=building_details.convenience_store if building_details else False,
                elevator=building_details.elevator if building_details else False,
                free_outdoor_parking=building_details.free_outdoor_parking if building_details else False,
                laundry_facilities=building_details.laundry_facilities if building_details else False,
                water_included=building_details.water_included if building_details else False,
                parking_cost=building_details.parking_cost if building_details else 0,
                parking_type=building_details.parking_type if building_details else '',
                walk_score=building_details.walk_score if building_details else 0,
                transit_score=building_details.transit_score if building_details else 0,
                bike_score=building_details.bike_score if building_details else 0,
                nearest_police_station=building_details.nearest_police_station if building_details else '',
                nearest_superstore=building_details.nearest_superstore if building_details else '',
                nearest_pharmacy=building_details.nearest_pharmacy if building_details else '',
                nearest_hospital=building_details.nearest_hospital if building_details else '',
                time_to_nearest_hospital=building_details.time_to_nearest_hospital if building_details else '',
                time_to_nearest_police_station=building_details.time_to_nearest_police_station if building_details else '',
                time_to_nearest_superstore=building_details.time_to_nearest_superstore if building_details else '',
                time_to_nearest_pharmacy=building_details.time_to_nearest_pharmacy if building_details else '',
                zone=building_details.zone if building_details else '',
                date=listing.date,
            )

    def process_westwood_listings():
        listings = WestwoodListings.objects.all()
        for listing in listings:
            # Check for existing entries in MasterPropertyData
            master_entry = MasterPropertyData.objects.filter(
                name=listing.title,
                bedrooms=listing.bedrooms,
                baths=listing.baths,
                size=listing.size,
                price_per_month=listing.price,
            ).order_by('-date').first()

            if master_entry:
                if not should_update(listing, master_entry):
                    continue

            # Get building details
            building_details = get_building_details(listing.title)

            # Create new master entry
            MasterPropertyData.objects.create(
                name=listing.title,
                builder_name=building_details.builder_name if building_details else '',
                status=building_details.status if building_details else '',
                address=listing.address,
                latitude=float(listing.latitude),
                longitude=float(listing.longitude),
                full_url=listing.full_url,
                image_urls='',  # Not available in Westwood data
                heat_included=listing.heat_included,
                hot_water_included=listing.hot_water_included,
                cat_allowed=False,  # Not available in Westwood data
                dog_allowed=False,  # Not available in Westwood data
                balcony=False,  # Not available in Westwood data
                in_building_laundry=False,  # Not available in Westwood data
                parking_available=listing.parking_available,
                gym_available=listing.gym_available,
                price_per_month=listing.price,
                bedrooms=listing.bedrooms,
                baths=listing.baths,
                size=listing.size,
                building_floor_plans='',
                hydro_included=False,  # Not available in Westwood data
                property_type=listing.property_type,
                price_per_sqft='',
                listing_address=listing.address,
                den_included=listing.den_included,
                parking=listing.parking,
                number_of_floors=building_details.number_of_floors if building_details else 0,
                number_of_units=building_details.number_of_units if building_details else 0,
                year_built=building_details.year_built if building_details else 0,
                air_conditioning=building_details.air_conditioning if building_details else False,
                balcony_patio=building_details.balcony_patio if building_details else False,
                convenience_store=building_details.convenience_store if building_details else False,
                elevator=building_details.elevator if building_details else False,
                free_outdoor_parking=building_details.free_outdoor_parking if building_details else False,
                laundry_facilities=building_details.laundry_facilities if building_details else False,
                water_included=building_details.water_included if building_details else False,
                parking_cost=building_details.parking_cost if building_details else 0,
                parking_type=building_details.parking_type if building_details else '',
                walk_score=building_details.walk_score if building_details else 0,
                transit_score=building_details.transit_score if building_details else 0,
                bike_score=building_details.bike_score if building_details else 0,
                nearest_police_station=building_details.nearest_police_station if building_details else '',
                nearest_superstore=building_details.nearest_superstore if building_details else '',
                nearest_pharmacy=building_details.nearest_pharmacy if building_details else '',
                nearest_hospital=building_details.nearest_hospital if building_details else '',
                time_to_nearest_hospital=building_details.time_to_nearest_hospital if building_details else '',
                time_to_nearest_police_station=building_details.time_to_nearest_police_station if building_details else '',
                time_to_nearest_superstore=building_details.time_to_nearest_superstore if building_details else '',
                time_to_nearest_pharmacy=building_details.time_to_nearest_pharmacy if building_details else '',
                zone=building_details.zone if building_details else '',
                date=listing.date,
            )

    # Entry point: Call the methods for processing listings
    process_killam_listings()
    process_templeton_listings()
    process_westwood_listings()

    return JsonResponse({"status": "success"}, status=200)
