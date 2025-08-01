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

            url = data["links"].get("next", None)

            if url:
                params = {}
            time.sleep(0.2)
        except requests.RequestException as e:
            print(f"Error fetching people: {e}")
            break
    return people_ids

def delete_birthdays():
    """Delete birthdays for all people by setting them to null."""
    people_ids = get_all_people()
    total = len(people_ids)

    print(f"Found {total} people to update birthdays.")

    if total == 0:
        print("No people to update.")
        return

    for i, person_id in enumerate(people_ids, 1):
        url = f"{BASE_URL}/people/{person_id}"
        data = {"data": {"type": "Person", "attributes": {"birthday": None}}}
        try:
            response = requests.patch(url, headers=HEADERS, auth=AUTH, json=data)
            if response.status_code == 200:
                print(f"[{i}/{total}] Updated birthday to null for person ID {person_id}")
            else:
                print(f"[{i}/{total}] Failed to update birthday for person ID {person_id}: {response.status_code} - {response.text}")
            time.sleep(0.2)
        except requests.RequestException as e:
            print(f"[{i}/{total}] Error updating person ID {person_id}: {e}")

if __name__ == "__main__":
    try:
        delete_birthdays()
    except Exception as e:
        print(f"An error occurred: {e}")
