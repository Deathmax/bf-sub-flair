import praw
import requests
import json
import io
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
        if len(parts) != 2:
            continue
        flairList[parts[0]] = parts[1]
    return flairList


def readConfig():
    return json.load(open('config.json'))


if __name__ == "__main__":
    printl('Starting bf-flair-bot')
    config = readConfig()
    r = praw.Reddit(user_agent='linux:com.deathsnacks.bravefrontier.flair:0.2-alpha (by /u/Deathmax)',
                    client_id=config['client_id'],
                    client_secret=config['client_secret'],
                    redirect_uri=config['redirect_uri'],
                    refresh_token=config['refresh_token'])

    printl('Logged in as: ' + str(r.user.me()))

    while True:
        try:
            printl('Fetching flair CSV')
            flairList = getFlairCsv()
            printl('Getting messages')
            messages = r.inbox.unread(mark_read=False, limit=30)
            for message in messages:
                print message
                if isinstance(message, praw.Comment):
                    message.mark_read()
                    continue
                if message.subject in flairList:
                    if (flairList[message.subject] == '*' or
                        flairList[message.subject] == message.author):
                        flairText = message.body
                        if flairText.lower() is 'none':
                            flairText = ''
                        r.subreddit('bravefrontier').flair.set(message.author, message.body, message.subject)
                        message.reply('_This is an automated message from the /r/bravefrontier bot._\n\nYour flair has been set to\'' + message.subject + '\'.')
                        printl('Set ' + message.author + ' flair to ' + message.subject + ' with text ' + flairText)
                    else:
                        message.reply('_This is an automated message from the /r/bravefrontier bot._\n\nSorry, you have no permission to set that flair.')
                        printl('Rejected set ' + message.author + ' flair to ' + message.subject + ' with text ' + message.body)
                message.mark_as_read()
            printl('Sleeping for 60 seconds')
            sleep(60)
        except KeyboardInterrupt:
            raise
        except Exception as e:
            printl('ERROR: ' + str(e))
