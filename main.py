#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
MIT License

Copyright (c) 2019

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE. 

'''
import os
import sys
import json
import argparse
from Oblivio import *

# Add commandline parameters when running Oblivio
argument_parser = argparse.ArgumentParser(
    description = '''Oblivio v.1.0 by Simon Olofsson.
                    See command switches below. For extensive
                    help on Oblivio, use the '-example' 
                    switch or visit URL HERE '''
)

# Add help strings to tuple
help_strings = (
    'See an example for how to use Oblivio',
    'Install directory for GAM',
    'Where Oblivio will store outputfiles',
    'Email adress for the GAM G suite user',
    'True or False. False will still create a local file.',
    'Remove the local file after upload.',
    '(int) Number of days unused for a device to be included. Default is 10.',
    'See the output from Oblivio in the shell. No upload or file creation.'
)

# Add commandline switches
argument_parser.add_argument('-example', help = help_strings[0])
argument_parser.add_argument('gampath', help = help_strings[1])
argument_parser.add_argument('outpath', help = help_strings[2])
argument_parser.add_argument('user', help = help_strings[3])
argument_parser.add_argument('-nofile', action = 'store_true', help = help_strings[4])
argument_parser.add_argument('-timedelta', help = help_strings[5])
argument_parser.add_argument('-verbose', action = 'store_true', help = help_strings[6])

# Parse all arguments given in to list object
ARGS = argument_parser.parse_args()

def verify_prereq(location):

    fail = None
    
    # Verify platform compatibility
    if not 'darwin' in sys.platform:
        err_handler(exception_type = Exception, task = 'platform')
        fail = True
    
    # Check that GAM resides in the directory
    if os.path.isfile(f'{location}') == False:
        err_handler(exception_type = Exception, task = 'gam_installed',)
        fail = True
    
    # Check that oauth2.txt file with credentials exists
    if os.path.isfile(f'{location}/oauth2.txt') == False:
        err_handler(exception_type = Exception, task = 'oauthfile')
        fail = True

    if not fail:
        return True

def get_user_id(filepath):
    ''' Return the username email for the authenticated 
    GAM user, stripped of the domain name to pass on to
    GAM. This is fetched if the 'default' parameter is
    given on the USER switch when Oblivio is run. '''
    try:
        with open(filepath) as _file:
            _user_id = json.load(_file)
            _user_id = _user_id.get('id_token')
            _user_id = _user_id.get('email')
    except:
        err_handler(exception_type = RuntimeError, task = 'get_user_id')
    else:
        # Strip the user name from domain to minimize leakage risk
        for index, i in enumerate(_user_id):
            if i == '@':
                _user_id[0:index - 1]
                break
        return _user_id

if __name__ == '__main__':
    
    # Verify that GAM and Oauth file is found
    ready = verify_prereq(ARGS.gampath)
    if ready == False:
        sys.exit()

    # If commandline argument is 'default' on user parameter, fetch it
    if ARGS.user == 'default':
        user_id = get_user_id(f'{ARGS.gampath}/oauth2.txt')
    else:
        user_id = ARGS.user

    # If timedelda is not set by commandline argument, use default
    if not ARGS.timedelta:
        __delta = 10
    else:
        __delta = ARGS.timedelta

    # Create instance of Inventory object and set properties
    oblivio = Inventory(delta = __delta, gam_path = f'{ARGS.gampath}')

    # Create instance of Localfile object to 
    file = Localfile(oblivio, ARGS.outpath, user_id)

    # If commandline argument '-verbose' is given, print to screen
    # and do not upload or create any files on the system.
if ARGS.verbose:
    print('\n','ALL DEVICES:', len(oblivio.inactive_devices), '\n')
    for i in oblivio.all_devices:
        print(i, end = '\n')

    print('\n','ACTIVE DEVICES:', len(oblivio.active_devices), '\n')
    for i in oblivio.active_devices:
        print(i, end = '\n')
    
    print('\n','INACTIVE DEVICES:', len(oblivio.inactive_devices),'\n')
    for i in oblivio.inactive_devices:
        print(i, end = '\n')
    
    print('\n','PROVISIONED DEVICES:', len(oblivio.provisioned), '\n')
    for i in oblivio.provisioned:
        print(i, end = '\n')
    
    print('\n','DEPROVISIONED DEVICES:', len(oblivio.deprovisioned), '\n')
    for i in oblivio.deprovisioned:
        print(i, end = '\n')
    
    print('\n','DISABLED DEVICES:', len(oblivio.disabled), '\n')
    for i in oblivio.disabled:
        print(i, end = '\n')
    
else:
    # If Verbose switch is not used, create the local file and upload it
    file_exists = file.create_file()
    if file_exists == True:
        upload_successful = file.upload_file()