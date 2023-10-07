import os
import requests
import json
import re
from dotenv import load_dotenv
import time
from argparse import ArgumentParser

load_dotenv()  # take environment variables from .env.

def get_content_length(payload):
    return str(len(json.dumps(payload)))

def create_headers(username, cookie, authorization, csrf_token):
    processed_cookie = ' '.join(line.strip() for line in cookie.split('\n') if line.strip())
    
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.9",
        "authorization": f"Bearer {authorization}",
        "content-type": "application/json",
        "cookie": processed_cookie,
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

# Create headers
headers = create_headers(username, cookie, authorization, csrf_token)

# Check if any of the environment variables are not set
if not all([cookie, authorization, csrf_token, username, graphqlId]):
    print("One or more environment variables are not set.")
    exit(1)
    
def unlike_tweet():
    # Check if the like.js file exists
    if not os.path.isfile("like.js"):
        print("The file like.js does not exist.")
        exit(1)
        
    # Check if the unliked.txt file exists
    if not os.path.isfile("unliked.txt"):
        with open('unliked.txt', 'x') as file:
            file.close()
        
    url = f"https://twitter.com/i/api/graphql/{graphqlId}/UnfavoriteTweet"
    
    # Load the data from like.js
    try:
        # Read the like.js file as a text
        with open('like.js', 'r') as file:
            js_text = file.read()
        
        json_str = js_text.replace('window.YTD.like.part0 = ', '', 1)
        tweets = json.loads(json_str)
    except IOError:
        print("An error occurred while trying to read the file like.js.")
        exit(1)

    # Extract tweet IDs from tweets
    tweet_ids = [tweet["like"]["tweetId"] for tweet in tweets]
    
    processor(url, tweet_ids, 'unliked.txt')
        
def delete_tweet():
    # Check if the tweets.js file exists
    if not os.path.isfile("tweets.js"):
        print("The file tweets.js does not exist.")
        exit(1)
    # Check if the deleted.txt file exists
    if not os.path.isfile("deleted.txt"):
        with open('deleted.txt', 'x') as file:
            file.close()
            
    url = f"https://twitter.com/i/api/graphql/{graphqlId}/DeleteTweet"
    
    # Load the data from tweets.js
    try:
        # Read the tweets.js file as a text
        with open('tweets.js', 'r') as file:
            js_text = file.read()
        
        json_str = js_text.replace('window.YTD.tweets.part0 = ', '', 1)
        tweets = json.loads(json_str)
    except IOError:
        print("An error occurred while trying to read the file tweets.js.")
        exit(1)

    # Extract tweet IDs from tweets
    tweet_ids = [tweet["tweet"]["id"] for tweet in tweets]
    
    processor(url, tweet_ids, 'deleted.txt')

def processor(url, tweet_ids, processor_bucket):
    data_length = len(tweet_ids)
    deleted_count = 0
    retries = 0
    
    while True:
        try:
            print(f'processed count: {deleted_count}')
            if deleted_count == data_length:
                print(f'Finished with {retries} retries')
                break
            for tweet_id in tweet_ids:
                with open(processor_bucket, 'r') as file:
                    items = [line.strip() for line in file]
                    if tweet_id in items:
                        deleted_count += 1
                        file.close()
                        continue
                    
                payload = {
                    "variables": {
                        "tweet_id": tweet_id,
                        "dark_request": False
                    },
                    "queryId": f"{graphqlId}"
                }
                
                headers["content-length"] = get_content_length(payload)
                
                # print(f'headers: {headers}')
                # print(f'url: {url}')
                
                response = requests.post(url, headers=headers, data=json.dumps(payload), timeout=15)

                if response.status_code == 200:
                    with open(processor_bucket, 'a') as file:
                        file.write(f'{tweet_id}\n')
                        file.close()
                    deleted_count += 1
                    print(f"Successfully deleted tweet with id: {tweet_id}")
                else:
                    print(f"Failed to delete tweet with id: {tweet_id}. Response code: {response.status_code}, Response message: {response.text}")
        except requests.exceptions.ConnectionError as e:
            print(f"Connection error: {e}, Retrying in 8 seconds.")
            retries += 1
            deleted_count = 0
            time.sleep(8)  # wait for 8 seconds before retrying
    
        
def main():
    # Create argument parser
    parser = ArgumentParser(description="Twitter Operations")
    parser.add_argument('--delete-tweet', action='store_true', help="Delete a tweet")
    parser.add_argument('--unlike', action='store_true', help="Unlike a tweet")

    args = parser.parse_args()

    # Perform actions based on command-line arguments
    if args.delete_tweet:
        delete_tweet()
    elif args.unlike:
        unlike_tweet()
    else:
        print("No valid action provided. Use --delete-tweet or --unlike.")


if __name__ == "__main__":
    main()