import urllib.request
import json
import os
from datetime import datetime, timedelta
import ssl


def fetch_and_merge(api_url, raw_file_path, reverse=False):
    try:
        with urllib.request.urlopen(api_url, context=context) as response:
            new_data = response.read().decode('utf-8')
            new_json = json.loads(new_data)

        if os.path.exists(raw_file_path):
            with open(raw_file_path, 'r', encoding='utf-8') as f:
                try:
                    existing_data = json.load(f)
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

        with open(raw_file_path, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, indent=2, ensure_ascii=False)

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

    # Ignore certificates because some APIs don't have a valid one
    context = ssl._create_unverified_context()

    print('Checking API availability...')
    for region in sources:
        region['available'] = check_api_availability(region)
        if not region['available']:
            print(f"Region {region['region']} is unavailable.")
        else:
            print(f'Removing old data from {region["region"]}...')
            remove_file(region['raw_file_path'])

    print('Fetching data...')
    for region in sources:
        if region['available']:
            print(f"Fetching data from {region['region']}...")
            fetch_region(region)

    print('Done.')
