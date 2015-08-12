#!/usr/bin/env python3

# Toggl Interface That Doesn't Suck

import os
import sys
import argh
import argparse
import re
import requests
import datetime
import tzlocal
import json

TOKEN_URL = 'https://www.toggl.com/app/profile'
API_URL   = 'https://www.toggl.com/api/v8/'
TOKEN_KEY = 'TOGGL_API_TOKEN'
DEBUG     = False

if not os.environ.get(TOKEN_KEY):
    print("You gotta export %s. Find yours at %s" % (TOKEN_KEY, TOKEN_URL))
    sys.exit(1)

API_AUTH = (os.environ.get(TOKEN_KEY), 'api_token')
HEADERS =  {'content-type': 'application/json'}


class MyAction(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest,
                 const,
                 default=None,
                 required=False,
                 help=None,
                 metavar=None):
        super(MyAction, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=0,
            const=const,
            default=default,
            required=required,
            help=help)

    # this gets called when -d/--debug is passed
    def __call__(self, parser, namespace, values, option_string=None):
        print_debug()
        pass



class TitdsError(Exception):
    pass

def print_debug():
    import http.client
    import urllib.parse
    """ this will print HTTP requests sent """
    # http://stackoverflow.com/questions/20658572/
    # python-requests-print-entire-http-request-raw
    global DEBUG
    DEBUG = True
    old_send = http.client.HTTPConnection.send
    def new_send( self, data ):
        print("REQUEST:")
        print(urllib.parse.unquote(data.decode()))
        return old_send(self, data)
    http.client.HTTPConnection.send = new_send

def req(url, params, method):
    _url = API_URL + url
    if method == "POST":
        response = requests.post(_url, auth=API_AUTH, headers=HEADERS, params=params)
    elif method == "GET":
        response = requests.get(_url, auth=API_AUTH, headers=HEADERS, params=params)
    else:
        raise TitdsError('GET or POST are the only supported request methods.')
    if DEBUG:
        print("RESPONSE:")
        print(response.status_code)
        print(json.dumps(response.json(), sort_keys=True, indent=4))

    if response.status_code != requests.codes.ok:
        response.raise_for_status()

    return response

@argh.aliases('l')
def time_entries():
    week_ago = datetime.datetime.now(tz=tzlocal.get_localzone()).replace(microsecond=0) - datetime.timedelta(days=7)
    params = {}
    params = {
        'start_date': week_ago.isoformat(),
        'end_date': datetime.datetime.now(tz=tzlocal.get_localzone()).replace(microsecond=0).isoformat()
    }

    print(req('time_entries', params, 'GET'))


if __name__ == "__main__":
    parser = argh.ArghParser()

    exposed = [time_entries]
    argh.assembling.set_default_command(parser, time_entries)

    parser.add_commands(exposed)
    parser.add_argument('-d', '--debug', const=False, action=MyAction)
    parser.dispatch() 
