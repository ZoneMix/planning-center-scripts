import requests
import time
import os
from requests.auth import HTTPBasicAuth

BASE_URL = "https://api.planningcenteronline.com/people/v2"
APPLICATION_ID = os.environ.get("PCO_APPLICATION_ID", "")
SECRET = os.environ.get("PCO_SECRET", "")
HEADERS = {
    "Content-Type": "application/json"
}
AUTH = HTTPBasicAuth(APPLICATION_ID, SECRET)

GRADES_FIELD_NAME = "Grade"
MEDICAL_NOTES_FIELD_NAME = "Medical Notes"

def get_all_people():
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
                print(person)
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
        response = requests.get(url, headers=HEADERS, auth=AUTH) #hparams=params)
        response.raise_for_status()
        data = response.json()
        print(data)
        if data["data"]:
            return data["data"][0]["id"]
        else:
            raise ValueError(f"Field definition '{field_name}' not found.")
    except requests.RequestException as e:
        print(f"Error fetching field definitions: {e}")
        raise

def delete_field_data_for_definition(field_definition_id):
    """Delete all field data for a given field definition ID."""
    url = f"{BASE_URL}/field_data"
    params = {"where[field_definition_id]": field_definition_id, "per_page": 100}
    while url:
        try:
            response = requests.get(url, headers=HEADERS, auth=AUTH, params=params)
            response.raise_for_status()
            data = response.json()
            for field_datum in data["data"]:
                delete_url = f"{BASE_URL}/field_data/{field_datum['id']}"
                delete_response = requests.delete(delete_url, headers=HEADERS, auth=AUTH)
                if delete_response.status_code == 204:
                    print(f"Deleted field datum ID {field_datum['id']}")
                else:
                    print(f"Failed to delete field datum ID {field_datum['id']}: {delete_response.status_code} - {delete_response.text}")
                time.sleep(0.2)
            url = data["links"].get("next", None)
            if url:
                params = {}
        except requests.RequestException as e:
            print(f"Error fetching field data: {e}")
            break

def delete_grades():
    """Delete grades field data for all people."""
    try:
        grades_field_id = get_field_definition_id(GRADES_FIELD_NAME)
        print(f"Deleting all grades field data (Field ID: {grades_field_id})...")
        delete_field_data_for_definition(grades_field_id)
    except ValueError as e:
        print(e)

def delete_medical_notes():
    """Delete medical notes field data for all people."""
    try:
        medical_notes_field_id = get_field_definition_id(MEDICAL_NOTES_FIELD_NAME)
        print(f"Deleting all medical notes field data (Field ID: {medical_notes_field_id})...")
        delete_field_data_for_definition(medical_notes_field_id)
    except ValueError as e:
        print(e)

if __name__ == "__main__":
    try:
        get_all_people()
    except Exception as e:
        print(f"An error occurred: {e}")
