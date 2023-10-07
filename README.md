# TweetBurner

This Python script allows for mass deletion of tweets without Twitter's API or password. The operation of the script hinges on utilizing the data from Twitter request headers, which can be accessed through the network tab of your browser's developer tools.

Before using this tool, you need to obtain your tweet archive file. This file can be requested from Twitter through your browser, but please note that it may take up to 24 hours for Twitter to generate your archive. Once you have received your archive, locate the 'tweets.js' file, as this is required for the script to function correctly.

The approach employed by this tool provides an additional level of security as it does not require access to sensitive data such as your Twitter password or API keys. However, it does require specific information from your request headers and tweet archive to work effectively.

This script provides a convenient alternative to manual tweet deletion or interfacing directly with Twitter's API, which may be complex for some users.

Please ensure to follow all guidelines and terms of service set by Twitter while using this script.

## Requirements

- Python 3.7 or newer
- Either pip (with or without a virtual environment) or conda for installing dependencies

## Getting Started

1. **Clone the repository**

    ```sh
    git clone https://github.com/utopictown/tweetburner.git
    cd tweetburner
    ```
2. **Prepare tweet list
   - Copy tweets.js from twitter archive to root directory
   - Copy like.js from twitter archive to root directory (needed if you want to do unlike as well)

3. **Set up the environment and install dependencies**

   - If you are using **pip** (optionally within a virtual environment), run:

        ```sh
        pip install -r requirements.txt
        ```

    - If you are using **conda**, run:

        ```sh
        conda env create -f environment.yml
        conda activate tweetburner
        ```

4. **Set up your environment variables**

    Create a file named `.env` in the root directory of the project and set the following variables. You can obtain these values from your browser's developer tools (Network tab) when making a request to Twitter (make sure you're authenticated first):

    ```sh
    cp .env.example .env
    ```

    OR

    ```env
    USERNAME=<your_twitter_username>
    COOKIE=<your_twitter_cookie>
    AUTHORIZATION=<your_twitter_bearer_token>
    CSRF_TOKEN=<your_twitter_csrf_token>
    GRAPHQL_ID=<your_twitter_graphql_id>
    ```

5. **Run the script**

    ```sh
    python main.py --delete-tweet
    python main.py --unlike
    ```

Please note that the use of this script should be in accordance with Twitter's terms of service.

## Disclaimer

This project is for educational purposes only. The user is responsible for their use of this tool and any consequences thereof. 
