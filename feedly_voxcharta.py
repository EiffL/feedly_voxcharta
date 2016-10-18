#!/usr/bin/python2
import requests
import ConfigParser
from urllib import quote
from bs4 import BeautifulSoup
import time
import os

sample_config = """
[feedly]
user_id = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx
token = YourAuthToken
newer_than = 24

[voxcharta]
institution = harvard
username = a_einstein
password = xxxxxxxxxx
"""

config_path = "~/.feedly_voxcharta/config.cfg"

feedly_url = "http://cloud.feedly.com/v3/"
voxcharta_url = "http://%s.voxcharta.org/"
voxcharta_login_url = "http://voxcharta.org/wp-login.php"

def get_feedly_arxiv_ids(user_id, token, newer_than=24):
    """
    Retrieves the list of recently marked arxiv id from feedly feed

    Parameters
    ----------
    user_id: string
        Feedly user id

    token: string
        Feedly personal developer token

    newer_than: int
        Number of hours in the past

    Returns
    -------
    arxivIds: list of strings
        List of arxiv id
    """
    headers={'Authorization':token}
    tag =u"user/"+user_id+"/tag/global.saved"
    qtag = quote(tag,safe="")

    # Get the list of tagged items
    r = requests.get(feedly_url+'streams/'+qtag+'/contents',
                     headers=headers,
                     params={'count':1000,
                             'newerThan': int(time.time() - newer_than*3600)*1000})

    # Get all the arxiv references
    arxivIds =[]
    for item in r.json()['items']:
        originId = item['originId']
        if 'arxiv.org' in originId:
            # We have identified a posting from arxiv, get the arxivID
            arxivIds.append(originId.split('/')[-1])
    return arxivIds

def get_voxcharta_postIDs(arxivIds, institution='harvard'):
    """
    Given a list of arxivIds, retrieves the voxcharta post ids
    in a convenient dictionary.

    Parameters
    ----------
    arxivIds: list of string
        List of arxiv ids to get a postID for.

    institution: string
        Institution to use for the subdomain on voxcharta

    Returns
    -------
    postIDs: dict
        Dictionary matching each arxiv id with a voxcharta post id
    """
    url = voxcharta_url%institution
    postIDs = {}

    # Query  voxcharta for eacuh id
    for arxivId in arxivIds:
        r = requests.get(url+'?s='+arxivId)
        if r.ok:
            soup = BeautifulSoup(r.content, "html.parser")
            s = soup.find('span',class_="additional-info")
            entryId = s['id'].split('-')[-1]
            # Check the corresponding link to make sure this is the right paper
            link = s.find('a')['href']
            if arxivId in link:
                postIDs[arxivId]=entryId
        else:
            print r.reason
    return postIDs

def upvote_voxcharta_postIDs(postIDs, username, password, institution='harvard'):
    """
    Upvote the given list of id on arxiv

    Parameters
    ----------
    postIDs: list of string
        IDs of the posts to upvote

    username: string
        voxcharta username

    password: string
        voxcharta password

    institution: string
        Institution to use for the subdomain on voxcharta

    Returns
    -------
    success: bool
        Return True if everything is successful
    """
    login_data = {'log':username,'pwd':password}

    # Upvote URL: vote_url%(userID,postID)
    vote_url = (voxcharta_url%institution)+"wp-content/plugins/vote-it-up/voteinterface.php?type=vote&tid=total&uid=%s&pid=%s&auth=0000"

    session = requests.Session()
    r = session.post(voxcharta_login_url, data=login_data)
    # Check successful login
    if 'wp-admin' in r.url and r.ok:
        print "Login successful !"
    else:
        print  "Error: couldn't login to voxcharta"
        return False

    # Extract user ID
    soup = BeautifulSoup(r.content, 'html.parser')
    uid = None
    for s in soup.find_all('script', type='text/javascript'):
        if 'userSettings' in s.text:
            uid =  s.text.split('"uid":"')[1].split('","')[0]
    if uid is None:
        print "Error: Couldn't retrieve userID"
        return False
    else:
        print "UserID: %s"%uid

    # Loop over postIDs and upvote them
    for pid in postIDs:
        r = session.get(vote_url%(uid,pid))
        if r.ok:
            print "Successfully upvoted postID %s"%pid
        else:
            print "Error when upvoting postID %s"%pid
            return False

    return True

# Main function
if __name__ == '__main__':
    # Check that the configuration exists
    if not os.path.isfile(os.path.expanduser(config_path)):
        print "Configuration file not found at default path: %s"%config_path
        print "Please create this file using the following template:"
        print "-----------------------------------------------------"
        print sample_config
        print "-----------------------------------------------------"
        exit(-1)

    config = ConfigParser.ConfigParser()
    config.read(os.path.expanduser(config_path))

    # Retrieve list of arxivIDs tagged in feedly in the last 24 hours
    arxivIDs = get_feedly_arxiv_ids(user_id=config.get('feedly','user_id'),
                                    token=config.get('feedly','token'),
                                    newer_than=int(config.get('feedly','newer_than')))

    # Get the corresponding postIDs on voxcharta
    postIDs = get_voxcharta_postIDs(arxivIDs, institution=config.get('voxcharta','institution'))

    print "Upvoting the following arxiv ids: ", postIDs.keys()

    success = upvote_voxcharta_postIDs(postIDs.values(),
                         username=config.get('voxcharta','username'),
                         password=config.get('voxcharta','password'),
                         institution=config.get('voxcharta','institution'))

    if success:
        print "Success !"
        exit(0)
    else:
        print  "Fail !"
        exit(-1)
