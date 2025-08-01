import requests
import time
import os
from requests.auth import HTTPBasicAuth

# Configuration
BASE_URL = "https://api.planningcenteronline.com/people/v2/people"
APPLICATION_ID = os.environ.get("PCO_APPLICATION_ID", "")
SECRET = os.environ.get("PCO_SECRET", "")
HEADERS = {
    "Content-Type": "application/json"
}
AUTH = HTTPBasicAuth(APPLICATION_ID, SECRET)

def get_all_people():
    """Fetch all people IDs with pagination."""
    people_ids = []
    url = BASE_URL
    params = {"per_page": 100}  # Max 100 per page per API docs

    while url:
        try:
            response = requests.get(url, headers=HEADERS, auth=AUTH, params=params)
            response.raise_for_status()
            data = response.json()

            # Extract IDs from current page
            for person in data["data"]:
                print(person)
                people_ids.append(person["id"])

            # Check for next page
            url = data["meta"].get("next", {}).get("href", None)

            # If next url exists, clear params
            if url:
                params = {}

            # Rate limit
            time.sleep(0.2)

        except requests.RequestException as e:
            print(f"Error fetching people: {e}")
            break

    return people_ids

def delete_person(person_id):
    """Delete a single person by ID."""
    url = f"{BASE_URL}/{person_id}"
    try:
        response = requests.delete(url, headers=HEADERS, auth=AUTH)
        if response.status_code == 204:
            print(f"Deleted person ID {person_id}")
        else:
            print(f"Failed to delete person ID {person_id}: {response.status_code} - {response.text}")
        time.sleep(0.2)
    except requests.RequestException as e:
        print(f"Error deleting person ID {person_id}: {e}")

def delete_all_people():
    """Delete all people records."""
    if not APPLICATION_ID or not SECRET:
        print("Error: Application ID or Secret not set in environment variables.")
        return

    print("Fetching all people IDs...")
    people_ids = get_all_people()
    total = len(people_ids)
    print(f"Found {total} people to delete.")

    if total == 0:
        print("No people to delete.")
        return

    confirm = input(f"Are you sure you want to delete all {total} people? This is irreversible! (yes/no): ")
    if confirm.lower() != "yes":
        print("Aborted.")
        return

    for i, person_id in enumerate(people_ids, 1):
        print(f"Deleting {i}/{total}...")

        # Choose to skip a person if desired
        #TODO make into CLI option
        if person_id == "ID_HERE":
            print(f"Skipping ID {person_id}")
        else:
            delete_person(person_id)

    print("Deletion process complete.")

if __name__ == "__main__":
    try:
        #TODO Change for CLI option to choose between the two
        #delete_person(12345678)
        #delete_all_people()
    except Exception as e:
        print(f"An error occurred: {e}")
