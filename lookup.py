import tweepy

# Set up Tweepy and authenticate with your Twitter API credentials
consumer_key = 'UZCAXwQzBuT1Z55HFnzFJBXOy'
consumer_secret = 'E0KVpqXC4soCy4vHV31MP6Ntmf0aDrCA5eug4WZmkJY4SCCfJW'
access_token = '752175431185420288-q42lQQoerFVuXPECcorSlrcPiAWlvku'
access_token_secret = 'R5Abol95ZOASfHyKi6qLhH1xDlGAvCQvhuCpvwroxwU7T'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

def lookup_user(username):
    try:
        user = api.get_user(screen_name=username)
        print(f"User ID: {user.id}")
        print(f"Name: {user.name}")
        print(f"Username: {user.screen_name}")
        print(f"Description: {user.description}")
        print(f"Location: {user.location}")
        print(f"Followers: {user.followers_count}")
        print(f"Following: {user.friends_count}")
        print(f"Profile Image URL: {user.profile_image_url_https}")
    except tweepy.TweepError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    username = input("Enter the username: ")
    lookup_user(username)