import twitter_credentials
import tweepy
from random import randint
import requests as req
import re
import time

auth = tweepy.OAuthHandler(twitter_credentials.CONSUMER_KEY, twitter_credentials.CONSUMER_SECRET)
auth.set_access_token(twitter_credentials.ACCESS_TOKEN, twitter_credentials.ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)
last_id_file_name = 'last_id.txt'
mode = 'Not Delete'

def read_last_answered_id():
    file = open(last_id_file_name, 'r')
    id = file.read().strip()
    file.close()
    if id != '':
        return int(id)
    return 0
    
def store_last_id(id):
    file = open(last_id_file_name, 'w')
    file.write(str(id))
    file.close()

def reply_saying(tweet):
    api.update_status('@' + tweet.user.screen_name + ' "' + get_new_saying() +'"', tweet.id)
    store_last_id(tweet.id)

def get_new_saying():
    resp_text = req.get("http://refranator.herokuapp.com/").text
    start = resp_text.index('<p>') + 3
    end = resp_text.index('</p>')
    saying = resp_text[start:end]
    return saying.strip()

def check_mentions():
    last_id = read_last_answered_id()
    if last_id > 0:
        mentions = api.mentions_timeline(last_id, tweet_mode = 'extended')
    else:
        mentions = api.mentions_timeline(tweet_mode = 'extended')
    print(str(len(mentions)) + ' new mention(s)')
    for tweet in reversed(mentions):
        reply_saying(tweet)

def batch_delete():
    print ("You are about to Delete all tweets from the account @%s." % api.verify_credentials().screen_name)
    if True:
        print('Deleting...')
        for status in tweepy.Cursor(api.user_timeline).items():
            try:
                api.destroy_status(status.id)
            except:
                print ('Failed to delete:', status.id)
    print('Tweets have been deleted.')

def main():
    if mode == 'Delete':
        batch_delete()
    else:
        print('Listening for new mentions...')
        while True:
            try:
                check_mentions()
            except tweepy.TweepError as e:
                raise e
            time.sleep(30)

if __name__ == '__main__':
    main()
