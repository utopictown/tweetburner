# TweetBurner

This Python script can be used to delete all of your tweets without using Twitter's API / password. It will need your twitter request headers data which you can find in network tab from browser. Please get tweet archive file which you can request from twitter (only on browser) before use (need to wait for 24 hours), we will need the tweets.js file to execute.

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
   - Replace tweets.json with tweets.js from twitter archive
   - delete `window.YTD.tweets.part0 = ` from file, the goal is to make it a valid .json file

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
    AUTHORIZATION=<your_twitter_authorization>
    CSRF_TOKEN=<your_twitter_csrf_token>
    GRAPHQL_ID=<your_twitter_graphql_id>
    ```

5. **Run the script**

    ```sh
    python main.py
    ```

Please note that the use of this script should be in accordance with Twitter's terms of service.

## Disclaimer

This project is for educational purposes only. The user is responsible for their use of this tool and any consequences thereof. 
