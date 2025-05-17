import urllib.request
import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import ssl
from pymongo import MongoClient
from dotenv import load_dotenv


def fetch_and_merge(api_url, raw_file_path, reverse=False):
    try:
        with urllib.request.urlopen(api_url, context=context) as response:
            new_data = response.read().decode('utf-8')
            new_json = json.loads(new_data)

        if os.path.exists(raw_file_path):
            with open(raw_file_path, 'r', encoding='utf-8') as fr:
                try:
                    existing_data = json.load(fr)
                except json.JSONDecodeError:
                    existing_data = []
        else:
            existing_data = []

        # Ensure new_json is a list; if not, convert it
        if not isinstance(new_json, list):
            new_json = [new_json]

        if reverse:
            new_json.reverse()

        merged_data = existing_data + new_json

        with open(raw_file_path, 'w', encoding='utf-8') as fw:
            json.dump(merged_data, fw, indent=2, ensure_ascii=False)

        return merged_data

    except Exception as e:
        print(f"Error fetching or merging data: {e}")
        return None


def fetch_region(region):
    api_params = '/api/?stavIds=210&stavIds=400&stavIds=410&stavIds=420&stavIds=430&stavIds=440&stavIds=500&stavIds=510&stavIds=520&stavIds=600&stavIds=610&stavIds=620&stavIds=700&stavIds=710&stavIds=750&stavIds=760&stavIds=780&stavIds=800'
    date_time = datetime(2005, 1, 1)

    while date_time < datetime.now():
        future_dt = date_time + timedelta(days=182.5)
        fetch_and_merge(
            region['url'] + api_params + f'&casOd={date_time.isoformat()}&casDo={future_dt.isoformat()}',
            region['raw_file_path'],
            True
        )
        date_time = future_dt


def fetch_units(region):
    def fetch_departure_units(departure):
        """
        Function to fetch units data for a single departure.
        Returns a tuple of (departure_id, units_json) for updating the original data.
        """
        try:
            url = f'{region['url']}/api/udalosti/{departure['id']}/technika'
            with urllib.request.urlopen(url, context=context) as response:
                units_data = response.read().decode('utf-8')
                units_json = json.loads(units_data)
                if not isinstance(units_json, list):
                    units_json = [units_json]
            return (departure['id'], units_json)
        except Exception as e:
            print(f"Error fetching data for departure {departure['id']}: {e}")
            return (departure['id'], [])

    try:
        if os.path.exists(region['raw_file_path']):
            with open(region['raw_file_path'], 'r', encoding='utf-8') as fr:
                try:
                    departures_data = json.load(fr)
                except json.JSONDecodeError:
                    departures_data = []
        else:
            departures_data = []

        if len(departures_data) > 0 and departures_data[0].get('sent_units') is not None:
            print(f'Skipping fetching units for {region["region"]} because they are already present')
            return departures_data

        max_workers = 20
        total_departures = len(departures_data)
        print(f"Starting to fetch data for {total_departures} departures with {max_workers} concurrent requests...")

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all tasks and store futures with their index for progress tracking
            futures = {executor.submit(fetch_departure_units, departure): i
                       for i, departure in enumerate(departures_data)
                       }

            # Process results as they complete
            completed_count = 0
            for future in as_completed(futures):
                idx = futures[future]
                completed_count += 1
                try:
                    departure_id, units_json = future.result()
                    # Update the original departures_data with the fetched units
                    for departure in departures_data:
                        if departure['id'] == departure_id:
                            departure['sent_units'] = units_json
                            break
                    print(
                        f"Fetched units {completed_count}/{total_departures} from region: {region['region']}",
                        f'{region['url']}/api/udalosti/{departure_id}/technika'
                    )
                except Exception as e:
                    print(f"Error processing departure at index {idx}: {e}")

        with open(region['raw_file_path'], 'w', encoding='utf-8') as fw:
            json.dump(departures_data, fw, indent=2, ensure_ascii=False)
            return departures_data

    except Exception as e:
        print(f"Error fetching or merging data: {e}")
        return None


def check_api_availability(region):
    try:
        with urllib.request.urlopen(region['url'], timeout=5, context=context) as response:
            return response.status == 200
    except Exception as e:
        print(f"Region {region['region']} is unavailable: {e}")
        return False


def remove_file(file_path):
    if os.path.exists(file_path):
        os.remove(file_path)


def format_departure_data(departure, region):
    departure_data = {
        "departure_id": departure["id"],
        "reportedDateTime": datetime.fromisoformat(departure["casOhlaseni"].replace('Z', '+00:00')),
        "startDateTime": departure["casVzniku"],
        "stateId": departure["stavId"],
        "typeId": departure["typId"],
        "subTypeId": departure["podtypId"],
        "description": departure["poznamkaProMedia"],
        "region_url": region['url'],
    }

    address_data = {
        "departure_id": departure["id"],
        "region": {
            "id": departure["kraj"]["id"],
            "name": departure["kraj"]["nazev"],
        },
        "district": {
            "id": departure["okres"]["id"],
            "name": departure["okres"]["nazev"],
        },
        "municipality": departure["obec"],
        "municipalityPart": departure["castObce"],
        "municipalityWithExtendedCompetence": departure["ORP"],
        "street": departure["ulice"],
        "gis1": departure["gis1"],
        "gis2": departure["gis2"],
        "preplanned": departure["zoc"],
        "road": departure["silnice"]
    }

    sent_units_data = [{
        "departure_id": departure["id"],
        "type": unit["typ"],
        "unit": unit["jednotka"],
        "count": unit["pocet"],
        "currentCount": unit["aktualniPocet"],
        "callDateTime": unit["casOhlaseni"]
    } for unit in departure['sent_units']]

    return departure_data, address_data, sent_units_data


def store_in_mongodb(departure_data, address_data, sent_units_data):
    client = MongoClient(mongo_url)
    db = client['fire_departures_db']

    departures_collection = db['departures']
    addresses_collection = db['addresses']
    sent_units_collection = db['sent_units']

    # Check if departure already exists
    if not departures_collection.find_one({"departure_id": departure_data["departure_id"]}):
        departures_collection.insert_one(departure_data)
        addresses_collection.insert_one(address_data)
        if len(sent_units_data) > 0:
            sent_units_collection.insert_many(sent_units_data)
        print(f"Inserted departure {departure_data['departure_id']}")
    else:
        print(f"Departure {departure_data['departure_id']} already exists")


def process_departures(region):
    if os.path.exists(region['raw_file_path']):
        with open(region['raw_file_path'], 'r', encoding='utf-8') as fr:
            try:
                departures_data = json.load(fr)
            except json.JSONDecodeError:
                departures_data = []
    else:
        departures_data = []

    for departure in departures_data:
        departure_data, address_data, units_data = format_departure_data(departure, region)
        store_in_mongodb(departure_data, address_data, units_data)


if __name__ == "__main__":
    sources = [
        {
            # 65457
            'region': 'Jihomoravský kraj',
            'url': 'https://udalosti.firebrno.cz',
            'raw_file_path': 'raw-data-jihomoravsky.json',
        },
        {
            'region': 'Královéhradecký kraj',
            'url': 'https://udalostikhk.hzscr.cz',
            'raw_file_path': 'raw-data-kralovehradecky.json',
        },
        {
            # 26477
            'region': 'Moravskoslezský kraj',
            'url': 'http://webohled.hzsmsk.cz',
            'raw_file_path': 'raw-data-moravskoslezsky.json',
        },
        {
            # 24126
            'region': 'Plzeňský kraj',
            'url': 'https://zasahy.hzspk.cz',
            'raw_file_path': 'raw-data-plzensky.json',
        },
        {
            # 6000
            'region': 'Ústecký kraj',
            'url': 'https://udalosti.hzsulk.cz',
            'raw_file_path': 'raw-data-ustecky.json',
        },
        {
            # 63392
            'region': 'Vysočina',
            'url': 'https://webohled.hasici-vysocina.cz/udalosti',
            'raw_file_path': 'raw-data-vysocina.json',
        },
        {
            'region': 'Zlínský kraj',
            'url': 'https://webohledzlk.hzscr.cz/udalosti',
            'raw_file_path': 'raw-data-zlinsky.json',
        }
    ]

    load_dotenv('../.env')

    mongo_ip = 'localhost'
    mongo_port1 = os.getenv('ROUTER_01_PORT')
    mongo_port2 = os.getenv('ROUTER_02_PORT')
    mongo_database = os.getenv('DATABASE_NAME')
    mongo_user = os.getenv('ROOT_USERNAME')
    mongo_password = os.getenv('ROOT_PASSWORD')

    mongo_url = f'mongodb://{mongo_user}:{mongo_password}@{mongo_ip}:{mongo_port1},{mongo_ip}:{mongo_port2}/{mongo_database}?authSource=admin'

    # Ignore certificates because some APIs don't have a valid one
    context = ssl._create_unverified_context()

    print('Checking API availability...')
    for region in sources:
        if os.path.exists(region['raw_file_path']):
            print(f'Skipping {region["region"]} because the data are already present')
            region['available'] = False
            continue
        else:
            region['available'] = check_api_availability(region)
        if not region['available']:
            print(f"Region {region['region']} is unavailable.")

    print('Fetching data...')
    for region in sources:
        if region['available']:
            print(f"Fetching data from {region['region']}...")
            fetch_region(region)

    print('Fetching units...')
    for region in sources:
        if region['available']:
            print(f"Fetching units from {region['region']}...")
            fetch_units(region)

    print('Formatting data and pushing to database...')
    for region in sources:
        if region['available']:
            print(f"Pushing data from {region['region']}...")
            process_departures(region)

    print('Done.')
