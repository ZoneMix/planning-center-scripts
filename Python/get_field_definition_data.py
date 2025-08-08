import requests
import time
import os
import argparse
from requests.auth import HTTPBasicAuth

BASE_URL = "https://api.planningcenteronline.com/people/v2"
APPLICATION_ID = os.environ.get("PCO_APPLICATION_ID", "")
SECRET = os.environ.get("PCO_SECRET", "")
HEADERS = {
    "Content-Type": "application/json"
}
AUTH = HTTPBasicAuth(APPLICATION_ID, SECRET)

def get_all_people_ids():
    """Fetch all people IDs with pagination."""
    people_ids = []
    url = f"{BASE_URL}/people"
    params = {"per_page": 100}  # Max 100 per page per API docs
    while url:
        try:
            response = requests.get(url, headers=HEADERS, auth=AUTH, params=params)
            response.raise_for_status()
            data = response.json()
            for person in data["data"]:
                people_ids.append(person["id"])
            # Check for next page in links
            url = data["links"].get("next", None)
            if url:
                params = {}  # Clear params for subsequent pages (URL has them)
            time.sleep(0.2)  # Basic rate limiting: 5 requests/sec
        except requests.RequestException as e:
            print(f"Error fetching people: {e}")
            break
    return people_ids

def get_field_definition_id(field_name):
    """Get field definition ID by name."""
    url = f"{BASE_URL}/field_definitions"
    params = {"where[name]": field_name}
    try:
        response = requests.get(url, headers=HEADERS, auth=AUTH, params=params)
        response.raise_for_status()
        data = response.json()
        if data["data"]:
            return data["data"][0]["id"]
        else:
            raise ValueError(f"Field definition '{field_name}' not found.")
    except requests.RequestException as e:
        print(f"Error fetching field definitions: {e}")
        raise

def get_field_data(field_definition_id):
    """Fetch all field data entries filtered by field_definition_id with pagination."""
    field_data = []
    url = f"{BASE_URL}/field_data"
    params = {
        "where[field_definition_id]": field_definition_id,
        "per_page": 100  # Max 100 per page per API docs
    }
    while url:
        try:
            response = requests.get(url, headers=HEADERS, auth=AUTH, params=params)
            response.raise_for_status()
            data = response.json()
            for entry in data["data"]:
                field_data.append({
                    "id": entry["id"],
                    "value": entry["attributes"]["value"],
                    "person_id": entry["relationships"]["customizable"]["data"]["id"]
                })
            # Check for next page in links
            url = data["links"].get("next", None)
            if url:
                params = {}  # Clear params for subsequent pages (URL has them)
            time.sleep(0.2)  # Basic rate limiting: 5 requests/sec
        except requests.RequestException as e:
            print(f"Error fetching field data: {e}")
            break
    return field_data

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Query Planning Center Online API")
    parser.add_argument(
        "--field",
        type=str,
        help="Name of the field definition to query (e.g., 'Grade' or 'Medical Notes')"
    )
    args = parser.parse_args()

    try:
        if args.field:
            field_id = get_field_definition_id(args.field)
            print(f"Field definition ID for '{args.field}': {field_id}")
            field_data = get_field_data(field_id)
            print(f"Data for field '{args.field}':")
            for entry in field_data:
                print(f"Person ID: {entry['person_id']}, Value: {entry['value']}, Field Data ID: {entry['id']}")
        else:
            people_ids = get_all_people_ids()
            print(f"Fetched {len(people_ids)} people IDs.")
    except Exception as e:
        print(f"An error occurred: {e}")
