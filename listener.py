import tweepy
import requests
from io import BytesIO
import cv2
import pytesseract
import re
import numpy as np
from PIL import Image
import pytesseract
import os
import json

# To set your enviornment variables in your terminal run the following line:
# export 'BEARER_TOKEN'='<your_bearer_token>'
# bearer_token = os.environ.get("BEARER_TOKEN")

consumer_key = 'ECH2k19iObLMcGfZ0AzjaGjFx'
consumer_secret = 'brnYuKkWZF4XdFlTTlwPmth3QmLXSGKgqBlaPITxaM7bRR7FXv'
access_token = '752175431185420288-cNSFjLej8to7uubsNPZikgm8Iuc4wIc'
access_token_secret = 'Y6ygdxSCaQEO0so7Yu789xXm5NI6jyZljanUQ30JtWiPt'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def post_tweet(WITH_URL, REPLY_ID):
    print("W URL: ", WITH_URL, "\n")
    print("REPLY: ", REPLY_ID, "\n")
    api.update_status(status = WITH_URL, in_reply_to_status_id=REPLY_ID)

def does_exist(username):
    try:
        user = api.get_user(screen_name=username)
        return True
    except tweepy.errors.TweepyException as e:
        return False

def search_tweets(username, search_text):
    search_query = f"from:{username} {search_text}"
    tweets = api.search_tweets(q=search_query, tweet_mode='extended', lang='en')

    if tweets:
        for tweet in tweets:
            tweet_url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
            return tweet_url
            print(f"Tweet URL: {tweet_url}")
            print(f"Tweet Text: {tweet.full_text}\n")
    else:
        print(f"No tweets found containing '{search_text}' from user {username}")

def extract_text_from_image(image_url):
    response = requests.get(image_url)
    # Load the image into OpenCV
    img_array = np.asarray(bytearray(response.content), dtype=np.uint8)
    img = cv2.imdecode(img_array, cv2.IMREAD_UNCHANGED)

    # Convert the image to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Extract text from the image using pytesseract
    text = pytesseract.image_to_string(gray)

    # Print the extracted text
    print(" ==== == Parsed text of: == ==== \n")
    print(text, "\n")
    print(" ==== == End Parsed text == ==== \n")


    print("==== Finding user's ID ==== ")
    results = []
    for i in range(len(text) - 1):
        if text[i] == "@" and text[i + 1].isalnum():
            j = i + 2
            temp_id = text[i]+text[i+1]
            while j < len(text) and text[j] != " " and text[j] != "\n" and (text[j].isalnum() or text[j] == "_"):
                temp_id += text[j]
                j += 1
            results.append(temp_id)

    ID_SET = set(results)
    print("Set : ", ID_SET)

    print("\n\n *** Attempting to find longest alphanumeric *** \n")

    SEQUENTIAL_TEXT = []
    for username in ID_SET: 

        pattern = re.compile(rf"{username}.*\n(.+)")
        match = pattern.search(text)

        if match:
            SEQUENTIAL_TEXT.append(match.group(1))
            print(f"String after {username}: {match.group(1)}")
        else:
            SEQUENTIAL_TEXT.append("")
            print(f"{username} not found")

    print("*** End of to find longest alphanumeric *** \n")
    print("==== End user's ID ==== \n")

    print("****")
    print("****")
    print("****")
    print("****")

    return ID_SET, SEQUENTIAL_TEXT

def find_tweet_sequence(reply_id):
    print("**** entering tweet sequence **** \n")
    # Get the reply tweet
    reply_tweet = api.get_status(reply_id, tweet_mode='extended')
    PHOTO_URLS = []
    if reply_tweet.in_reply_to_status_id is not None:
        # Get the parent tweet using in_reply_to_status_id
        parent_tweet_id = reply_tweet.in_reply_to_status_id
        parent_tweet = api.get_status(parent_tweet_id, tweet_mode='extended')

        # Check if the parent tweet has an image
        if 'media' in parent_tweet.extended_entities:
            for media in parent_tweet.extended_entities['media']:
                if media['type'] == 'photo':
                    image_url = media['media_url']
                    PHOTO_URLS.append(image_url)
                    print("The parent tweet has an image with the URL:", image_url)
        else:
            print("The parent tweet does not have an image.")
    else:
        print("The given tweet is not a reply.")
    for THIS_URL in PHOTO_URLS:
        ids, contents = extract_text_from_image(THIS_URL)
        index = 0
        for username in ids: 
            if does_exist(username):
                print("Username of ", username, " does exist\n")
                if contents[index] != "":
                    ORIGINAL_URL = search_tweets(username, contents[index])
                    post_tweet(ORIGINAL_URL, reply_id)
            else:
                print(username, "does not exist. They may have changed their username or deactivated their account")
            index += 1


def bearer_oauth(r):
    """
    Method required by bearer token authentication.
    """

    r.headers["Authorization"] = f"Bearer AAAAAAAAAAAAAAAAAAAAANFNmQEAAAAAGCfr%2BWDtKvvnKw%2FYaNMv8vaVHjc%3DXQqWVeL6PLL0hqC3tasQYv7Haz0MUJHbJBmP3Y6roLxj3tPMhH"
    r.headers["User-Agent"] = "v2FilteredStreamPython"
    return r


def get_rules():
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream/rules", auth=bearer_oauth
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot get rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))
    return response.json()


def delete_all_rules(rules):
    if rules is None or "data" not in rules:
        return None

    ids = list(map(lambda rule: rule["id"], rules["data"]))
    payload = {"delete": {"ids": ids}}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload
    )
    if response.status_code != 200:
        raise Exception(
            "Cannot delete rules (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    print(json.dumps(response.json()))


def set_rules(delete):
    # You can adjust the rules if needed
    # sample_rules = [
    #     {"value": "dog has:images", "tag": "dog pictures"},
    #     {"value": "cat has:images -grumpy", "tag": "cat pictures"},
    # ]
    sample_rules = [
        {"value": "@findsaucebot", "tag": "bot_mentioned"},
    ]
    payload = {"add": sample_rules}
    response = requests.post(
        "https://api.twitter.com/2/tweets/search/stream/rules",
        auth=bearer_oauth,
        json=payload,
    )
    if response.status_code != 201:
        raise Exception(
            "Cannot add rules (HTTP {}): {}".format(response.status_code, response.text)
        )
    print(json.dumps(response.json()))


def get_stream(set):
    response = requests.get(
        "https://api.twitter.com/2/tweets/search/stream", auth=bearer_oauth, stream=True,
    )
    print(response.status_code)
    if response.status_code != 200:
        raise Exception(
            "Cannot get stream (HTTP {}): {}".format(
                response.status_code, response.text
            )
        )
    for response_line in response.iter_lines():
        # print("Response line is: ", response_line)
        if response_line:
            json_response = json.loads(response_line)
            # print("JS response: ", json_response)
            print("Data is ", json_response["data"]["id"])
            TWEET_ID = json_response["data"]["id"]
            find_tweet_sequence(TWEET_ID)
            print("JSON DUMP: ", json.dumps(json_response, indent=4, sort_keys=True))


def main():
    rules = get_rules()
    delete = delete_all_rules(rules)
    set = set_rules(delete)
    get_stream(set)


if __name__ == "__main__":
    main()


# print("Reply tweet is: ", reply_tweet, "\n")
# Check if the tweet is a reply
# if reply_tweet.in_reply_to_status_id is not None:
#     # Get the parent tweet using in_reply_to_status_id
#     parent_tweet_id = reply_tweet.in_reply_to_status_id
#     parent_tweet = api.get_status(parent_tweet_id, tweet_mode='extended')
#     print("Parent Tweet is: ", parent_tweet, "\n")
#     print("\n**** ending tweet sequence IF!! **** \n")
#     return parent_tweet
# print("\n**** ending tweet sequence NOIF **** \n")
# Check if the tweet is a reply