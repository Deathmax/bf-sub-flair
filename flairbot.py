import praw
import requests
from time import sleep
from datetime import datetime


def printl(msg):
    print '[' + str(datetime.now()) + ']' + ' ' + str(msg)


def getFlairCsv():
    r = requests.get('https://jscheah.me/bf-sub-flair/flairlist.csv')
    lines = r.text.split('\n')
    flairList = {}
    for line in lines:
        parts = line.split(',')
        flairList[parts[0]] = parts[1]
    return flairList


if __name__ == "__main__":
    printl('Starting bf-flair-bot')
    user_agent = "linux:com.deathsnacks.bravefrontier.flair:0.1-alpha (by /u/Deathmax)"
    r = praw.Reddit(user_agent=user_agent)
    r.set_oauth_app_info(client_id="CID",
                         client_secret="SECRET",
                         redirect_uri="REDIRECT_URI")
    
    access_information = {u'access_token': u'ACCESS_TOKEN', 
                          u'scope': set([u'wikiedit', u'privatemessages', u'modflair', u'identity', u'flair']), 
                          u'refresh_token': u'REFRESH_TOKEN'}
    
    r.set_access_credentials(**access_information)
    authenticated_user = r.get_me()
    printl('Logged in as: ' + authenticated_user.name)
    
    while True:
        try:
            printl('Fetching flair CSV')
            flairList = getFlairCsv()
            printl('Getting messages')
            messages = r.get_unread(False, False, limit=30)
            for message in messages:
                print message
                if message.was_comment:
                    message.mark_read()
                    continue
                if message.subject in flairList:
                    if (flairList[message.subject] == '*' or
                        flairList[message.subject] == message.author):
                        flairText = message.body
                        if flairText.lower() is 'none':
                            flairText = ''
                        r.get_subreddit('bravefrontier').set_flair(message.author, message.body, message.subject)
                        message.reply('_This is an automated message from the /r/bravefrontier bot._\n\nYour flair has been set to\'' + message.subject + '\'.')
                        printl('Set ' + message.author + ' flair to ' + message.subject + ' with text ' + flairText)
                    else:
                        message.reply('_This is an automated message from the /r/bravefrontier bot._\n\nSorry, you have no permission to set that flair.')
                        printl('Rejected set ' + message.author + ' flair to ' + message.subject + ' with text ' + message.body)
                message.mark_read()
            printl('Sleeping for 60 seconds')
            sleep(60)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            printl('ERROR: ' + str(e))
