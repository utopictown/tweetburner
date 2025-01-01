import os
import requests
import json
import re
from dotenv import load_dotenv
import time
from argparse import ArgumentParser
from datetime import datetime

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
    
def load_tweets(file_path):
    try:  
        file_name = file_path.split('/')[-1]
        type = file_name.split('.')[0]
        if not type:
            raise Exception(f"Type is not specified")
        # Check if the like.js file exists
        if not os.path.isfile(file_path):
            raise Exception(f"The file {file_path} does not exist.")
        with open(file_path, 'r') as file:
            js_text = file.read()
        
        json_str = js_text.replace(f"window.YTD.{type}.part0 = ", '', 1)
        tweets = json.loads(json_str)
        return tweets
    except IOError:
        print("An error occurred while trying to read the file")
        exit(1)
    except Exception as e:
        print(e)
        exit(1)

def filter_tweets(tweets, start_date, end_date=None):
    filtered_tweets = []
    if not start_date:
        return tweets
    # Set default value for end_date to today if not provided
    if end_date is None:
        end_date = datetime.today()
    for tweet in tweets:
        tweet_date = datetime.strptime(tweet['tweet']['created_at'], "%a %b %d %H:%M:%S +0000 %Y")
        if (start_date is None or tweet_date >= start_date) and (end_date is None or tweet_date <= end_date):
            filtered_tweets.append(tweet)
    return filtered_tweets
    
def unlike_tweet(exclude_ids):
    url = f"https://twitter.com/i/api/graphql/{graphqlId}/UnfavoriteTweet"
    tweets = load_tweets('like.js')
    # Check if the unliked.txt file exists
    if not os.path.isfile("unliked.txt"):
        with open('unliked.txt', 'x') as file:
            file.close()

    # Extract tweet IDs from tweets
    tweet_ids = [tweet["like"]["tweetId"] for tweet in tweets]
    
    processor(url, tweet_ids, 'unliked.txt', exclude_ids)
        
def delete_tweet(exclude_ids, start_date, end_date):
    url = f"https://twitter.com/i/api/graphql/{graphqlId}/DeleteTweet"
    tweets = load_tweets('tweets.js')
    # Check if the deleted.txt file exists
    if not os.path.isfile("deleted.txt"):
        with open('deleted.txt', 'x') as file:
            file.close()
            
    filtered_tweets = filter_tweets(tweets, start_date, end_date)

    # Extract tweet IDs from tweets
    tweet_ids = [tweet["tweet"]["id"] for tweet in filtered_tweets]
    
    processor(url, tweet_ids, 'deleted.txt', exclude_ids)

def processor(url, tweet_ids, processor_bucket, exclude_ids):
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
                if tweet_id in exclude_ids:
                    print(f"Skipping excluded tweet with id: {tweet_id}")
                    deleted_count += 1
                    continue
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
    parser.add_argument('--exclude', help="Comma-separated list of tweet IDs to exclude")
    parser.add_argument('--start-date', type=str, help="Start date for filtering tweets (YYYY-MM-DD)")
    parser.add_argument('--end-date', type=str, help="End date for filtering tweets (YYYY-MM-DD)")

    args = parser.parse_args()
    
    exclude_ids = args.exclude.split(',') if args.exclude else []
    
    start_date = datetime.strptime(args.start_date, "%Y-%m-%d") if args.start_date else None
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d") if args.end_date else None

    # Perform actions based on command-line arguments
    if args.delete_tweet:
        delete_tweet(exclude_ids, start_date, end_date)
    elif args.unlike:
        unlike_tweet(exclude_ids, start_date, end_date)
    else:
        print("No valid action provided. Use --delete-tweet or --unlike.")


if __name__ == "__main__":
    main()