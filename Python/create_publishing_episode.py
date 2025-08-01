import os
import json
import requests
from requests.auth import HTTPBasicAuth

BASE_URL = "https://api.planningcenteronline.com/publishing/v2"
APPLICATION_ID = os.environ.get("PCO_APPLICATION_ID", "")
SECRET = os.environ.get("PCO_SECRET", "")
HEADERS = {
    "Content-Type": "application/json"
}
AUTH = HTTPBasicAuth(APPLICATION_ID, SECRET)

def get_channel():
    url = BASE_URL + "/channels"
    params = { "order": "name"}
    response = requests.get(url, headers=HEADERS, auth=AUTH, params=params)
    return response.json()['data'][0]['id']


def create_example_episode():
    channel_id = get_channel()
    url = BASE_URL + f"/channels/{channel_id}/episodes"
    data = {
        "data": {
            "attributes": {
                "title": "New Episode"
            }
        }
    }
    response = requests.post(url, headers=HEADERS, auth=AUTH, json=data)
    return response.json()

if __name__ == "__main__":
    episode = create_example_episode()
    print(episode)
