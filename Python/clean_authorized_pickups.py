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

def get_field_definition_id(field_name="Authorized Pickup"):
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
                    "value": entry["attributes"]["value"].split(","),
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

def update_field_data(field_data_entry, field_definition_id):
    """Update the value of a specific field_data entry using PATCH."""
    field_data_id = field_data_entry["id"]
    names = field_data_entry["value"]
    url = f"{BASE_URL}/field_data/{field_data_id}"

    payload = {
        "data": {
            "attributes": {
                "field_definition_id": field_definition_id,
                "value": names
            }
        }
    }
    try:
        response = requests.patch(url, headers=HEADERS, auth=AUTH, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["data"]["attributes"]["value"]
    except requests.RequestException as e:
        raise

def create_field_data(field_data_entry, field_definition_id):
    """Update the value of a specific field_data entry using POST."""
    names = field_data_entry["value"]
    person_id = field_data_entry["person_id"]
    url = f"{BASE_URL}/people/{person_id}/field_data"

    payload = {
        "data": {
            "attributes": {
                "field_definition_id": field_definition_id,
                "value": names
            }
        }
    }
    try:
        response = requests.post(url, headers=HEADERS, auth=AUTH, json=payload)
        response.raise_for_status()
        data = response.json()
        return data["data"]["attributes"]["value"]
    except requests.RequestException as e:
        pass

def delete_field_data(field_data_entry):
    """Update the value of a specific field_data entry using POST."""
    field_data_id = field_data_entry["id"]
    url = f"{BASE_URL}/field_data/{field_data_id}"

    try:
        response = requests.delete(url, headers=HEADERS, auth=AUTH)
        response.raise_for_status()
        data = response.json()
        return data["data"]["attributes"]["value"]
    except requests.RequestException as e:
        pass
    
def search_person_by_name(search_name):
    """Search for a person by name and return their ID."""
    url = f"{BASE_URL}/people"
    params = {"where[search_name]": search_name, "per_page": 100}
    try:
        response = requests.get(url, headers=HEADERS, auth=AUTH, params=params)
        response.raise_for_status()
        data = response.json()
        people = data["data"]

        id = people[0]["id"]

        email_url = f"{url}/{id}/emails"
        response = requests.get(email_url, headers=HEADERS, auth=AUTH, params=params)
        response.raise_for_status()
        data = response.json()
        email = data["data"][0]["attributes"]["address"]

        phone_url = f"{url}/{id}/phone_numbers"
        response = requests.get(phone_url, headers=HEADERS, auth=AUTH, params=params)
        response.raise_for_status()
        data = response.json()
        phone = data["data"][0]["attributes"]["number"]

        return email, phone
    except:
        return 0, 0

if __name__ == "__main__":
    try:
        auth_pickup = get_field_definition_id("Authorized Pickups")
        auth_pickup_parsed = get_field_definition_id("Authorized Pickups Parsed")
        field_data = get_field_data(auth_pickup)
        for entry in field_data:
            i = 0
            while '' in entry["value"]:
                entry["value"].remove('')
            for name in entry["value"]:
                email, phone = search_person_by_name(name)
                entry["value"][i] = f"{name};{email};{phone}"
                i = i + 1
            entry["value"] = '|'.join(n for n in entry["value"])
            if "|" not in entry["value"]:
                entry["value"] = entry["value"] + "|"

            print(entry)
            create_field_data(entry, auth_pickup_parsed)

    except Exception as e:
        print(f"An error occurred: {e}")
