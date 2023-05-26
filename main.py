import os
import requests
import json
import re
from dotenv import load_dotenv

load_dotenv()  # take environment variables from .env.

def get_content_length(payload):
    return str(len(json.dumps(payload)))

def create_headers(username, cookie, authorization, csrf_token):
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {authorization}",
        "content-type": "application/json",
        "cookie": cookie,
        "origin": "https://twitter.com",
        "referer": f"https://twitter.com/{username}",
        "sec-ch-ua": '"Microsoft Edge";v="113", "Chromium";v="113", "Not-A.Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "macOS",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.50",
        "x-client-uuid": "e4b14c75-5af6-45c5-9abb-045eac507376",
        "x-csrf-token": csrf_token,
        "x-twitter-active-user": "yes",
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-client-language": ""
    }
    return headers

# please see your twitter request headers to get the values for the following variables in browser dev tools
cookie = os.getenv("COOKIE")
authorization = os.getenv("AUTHORIZATION")
csrf_token = os.getenv("CSRF_TOKEN")
username = os.getenv("USERNAME")
graphqlId = os.getenv("GRAPHQLID")

# Check if any of the environment variables are not set
if not all([cookie, authorization, csrf_token, username, graphqlId]):
    print("One or more environment variables are not set.")
    exit(1)

url = f"https://twitter.com/i/api/graphql/{graphqlId}/DeleteTweet"

# Check if the tweets.json file exists
if not os.path.isfile("tweets.json"):
    print("The file tweets.json does not exist.")
    exit(1)

# Load the data from tweets.json
try:
    with open("tweets.json", "r") as file:
        tweets = json.load(file)
except IOError:
    print("An error occurred while trying to read the file tweets.json.")
    exit(1)

# Extract tweet IDs from tweets
tweet_ids = [tweet["tweet"]["id"] for tweet in tweets]

headers = create_headers(username, cookie, authorization, csrf_token)

for tweet_id in tweet_ids:
    payload = {
        "variables": {
            "tweet_id": tweet_id,
            "dark_request": False
        },
        "queryId": f"{graphqlId}"
    }
    
    headers["content-length"] = get_content_length(payload)
    
    response = requests.post(url, headers=headers, data=json.dumps(payload))

    if response.status_code == 200:
        print(f"Successfully deleted tweet with id: {tweet_id}")
    else:
        print(f"Failed to delete tweet with id: {tweet_id}. Response code: {response.status_code}, Response message: {response.text}")
