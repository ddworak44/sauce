import tweepy
import requests
from io import BytesIO
import cv2
import pytesseract
import re

# Set up Tweepy and authenticate with your Twitter API credentials
consumer_key = 'your_consumer_key'
consumer_secret = 'your_consumer_secret'
access_token = 'your_access_token'
access_token_secret = 'your_access_token_secret'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# Define a function to extract text from an image using OpenCV and pytesseract
def extract_text_from_image(image_url):
    response = requests.get(image_url)
    img = cv2.imdecode(np.frombuffer(response.content, np.uint8), cv2.IMREAD_UNCHANGED)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    text = pytesseract.image_to_string(gray)
    return text

# Define a function to extract the original tweet URL
def extract_tweet_url(tweet_text):
    username_pattern = r'@(\w+)'
    tweet_id_pattern = r'twitter.com/(\w+)/status/(\d+)'

    username = re.search(username_pattern, tweet_text)
    tweet_id = re.search(tweet_id_pattern, tweet_text)

    if username and tweet_id:
        tweet_url = f"https://twitter.com/{username.group(1)}/status/{tweet_id.group(2)}"
        return tweet_url
    return None

# Define a class that extends tweepy.StreamListener to handle incoming mentions
class MyStreamListener(tweepy.StreamListener):
    def on_status(self, status):
        if status.in_reply_to_screen_name == 'your_bot_screen_name':
            if 'media' in status.entities:
                image_url = status.entities['media'][0]['media_url']
                tweet_image_text = extract_text_from_image(image_url)
                original_tweet_url = extract_tweet_url(tweet_image_text)

                if original_tweet_url:
                    api.update_status(
                        f"@{status.user.screen_name} The original tweet: {original_tweet_url}",
                        in_reply_to_status_id=status.id
                    )
                else:
                    api.update_status(
                        f"@{status.user.screen_name} Sorry, I couldn't find the original tweet.",
                        in_reply_to_status_id=status.id
                    )

# Start streaming and processing mentions
myStreamListener = MyStreamListener()
myStream = tweepy.Stream(auth=api.auth, listener=myStreamListener)
myStream.filter(track=['@your_bot_screen_name'])