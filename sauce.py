import tweepy
import requests
from io import BytesIO
import cv2
import pytesseract
import re
import numpy as np
from PIL import Image
import pytesseract

# Set up Tweepy and authenticate with your Twitter API credentials

consumer_key = 'UZCAXwQzBuT1Z55HFnzFJBXOy'
consumer_secret = 'E0KVpqXC4soCy4vHV31MP6Ntmf0aDrCA5eug4WZmkJY4SCCfJW'
access_token = '752175431185420288-q42lQQoerFVuXPECcorSlrcPiAWlvku'
access_token_secret = 'R5Abol95ZOASfHyKi6qLhH1xDlGAvCQvhuCpvwroxwU7T'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

BOT_USERNAME = "ddforpresident"

# Define a function to extract text from an image using OpenCV and pytesseract
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


        # pattern = re.compile(rf"{username}\n\n(.+)")
        # print("Using pattern of: ", pattern)
        # match = pattern.search(text)
        # print("Where match is: ", match)

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

def search_tweets(username, search_text):
    search_query = f"from:{username} {search_text}"
    tweets = api.search_tweets(q=search_query, tweet_mode='extended', lang='en')

    if tweets:
        for tweet in tweets:
            tweet_url = f"https://twitter.com/{tweet.user.screen_name}/status/{tweet.id}"
            print(f"Tweet URL: {tweet_url}")
            print(f"Tweet Text: {tweet.full_text}\n")
    else:
        print(f"No tweets found containing '{search_text}' from user {username}")

def does_exist(username):
    try:
        user = api.get_user(screen_name=username)
        # print(f"Account with username '{username}' exists.")
        return True
    except tweepy.errors.TweepyException as e:
        # print(" ** Printing User not Found Code ** ")
        # print(e)
        # print(" ** End of User not Found Code ** ")
        return False
        # if e.api_code == 50 or e.api_code == 63:
        #     print(f"Account with username '{username}' does not exist or is suspended.")
        #     return False
        # else:
        #     print("An error occurred:", e)
        #     return None


if __name__ == "__main__":

    # "Consumer Key here", "Consumer Secret here",
    # "Access Token here", "Access Token Secret here"
    stream = tweepy.Stream(
        consumer_key, consumer_secret, access_token, access_token_secret
    )

    # Filter the stream to listen for replies to your bot's account
    stream.filter(track=[f"@{BOT_USERNAME}"], is_async=True)

    THIS_URL = input("Enter a valid URL: ")
    ids, contents = extract_text_from_image(THIS_URL)
    print("Ids are: ", ids)
    print("Contents are: ", contents)

    index = 0
    for username in ids: 
        if does_exist(username):
            print("Username of ", username, " does exist\n")
            if contents[index] != "":
                search_tweets(username, contents[index])
        else:
            print(username, "does not exist. They may have changed their username or deactivated their account")
        
        index += 1
        # if (contents[index] == ""):
        #     continue 
        # found_it = search_tweets(username, contents[index])
        # print(found_it)
        # index += 1



# Define a function to extract the original tweet URL
# def extract_tweet_url(tweet_text):
#     username_pattern = r'@(\w+)'
#     tweet_id_pattern = r'twitter.com/(\w+)/status/(\d+)'

#     username = re.search(username_pattern, tweet_text)
#     tweet_id = re.search(tweet_id_pattern, tweet_text)

#     if username and tweet_id:
#         tweet_url = f"https://twitter.com/{username.group(1)}/status/{tweet_id.group(2)}"
#         return tweet_url
#     return None

# Define a class that extends tweepy.StreamListener to handle incoming mentions
# class MyStreamListener(tweepy.StreamListener):
#     def on_status(self, status):
#         if status.in_reply_to_screen_name == 'your_bot_screen_name':
#             if 'media' in status.entities:
#                 image_url = status.entities['media'][0]['media_url']
#                 tweet_image_text = extract_text_from_image(image_url)
#                 original_tweet_url = extract_tweet_url(tweet_image_text)

#                 if original_tweet_url:
#                     api.update_status(
#                         f"@{status.user.screen_name} The original tweet: {original_tweet_url}",
#                         in_reply_to_status_id=status.id
#                     )
#                 else:
#                     api.update_status(
#                         f"@{status.user.screen_name} Sorry, I couldn't find the original tweet.",
#                         in_reply_to_status_id=status.id
#                     )

# Start streaming and processing mentions
# myStreamListener = MyStreamListener()
# myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
# myStream.filter(track=['@your_bot_screen_name'])


# for element in ID_SET: 
#     #     print("E is: ", element)
#     #     match = re.search(rf"{re.escape(element)}\s*(\w+)", text)
#     #     if match:
#     #         longest_alphanumeric = max(re.findall(r'\w+', match.group(1)), key=len)
#     #         print(f"The next longest alphanumeric string after {element} is [ {longest_alphanumeric} ]")
