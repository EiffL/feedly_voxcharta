# feedly_voxcharta

Simple script to upvote papers on voxcharta from list of papers tagged on feedly.

DISCLAIMER: USE WITH CAUTION, THE VOXCHARTA INTERACTIONS DO NOT RELY ON AN API BUT INSTEAD ON A MANUAL PARSING OF THE 
WEBSITE AND COULD EASILY BREAK. USE AT YOUR OWN RISKS !!!

[Feedly](https://feedly.com) is a nice feed aggregator that you can use to manage your daily arxiv feed. Once you have subscribed to an arXiv feed, you can easily
tag the papers you find interesting.

This script will look for the arXiv papers you have recently tagged in feedly and
automatically upvote them on voxcharta for you.

## Get authentification on feedly

In order to connect to feedly through the Feedly Cloud API, you need to request
a user_id and associated authentification token at this address: http://feedly.com/v3/auth/dev

With this personal developer token you can make up to 250 API requests per day
but they only last for 30 days. More info here: https://developer.feedly.com/v3/developer/

## Register on voxcharta

If you don't already have one, you need an account on voxcharta. Just register
on the subdomain corresponding to your institution.

## Setting up the configuration file

This script expects your authentification information to be placed inside a
configuration file in *~/.feedly_voxcharta/config.cfg* with the following content:

    [feedly]
    user_id = xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxx
    token = YourAuthToken
    newer_than = 24

    [voxcharta]
    institution = harvard
    username = a_einstein
    password = xxxxxxxxxx

## Running the script

Once the configuration file is in place, running  this script  should be as simple as this:

    python2 feedly_voxcharta.py

If you want the script to be run periodically to update your voxcharta votes,
you can set up a cron job, running for instance once every day.
