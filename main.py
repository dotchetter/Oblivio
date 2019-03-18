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

<<<<<<< HEAD
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
=======
# Set GAM as installed in default directory in user's $home.
GAM = os.getenv("HOME") + '/bin/gam/gam'
# Set GAMDIR as the directory where GAM is installed per default
GAMDIR = GAM.strip('gam')
# Set Oblivio dir inside the GAM dir
OBLIVIODIR = GAMDIR + 'Oblivio'

def main():
    
>>>>>>> 620da4a9805a947ad72a1123aac081e62ccfa2ff
    assert (
        'darwin' in sys.platform
    ), err_handler(exception_type = Exception, task = 'platform')
    
    # Check that GAM resides in the presumed directory
<<<<<<< HEAD
    if not 'win32' in sys.platform:
        err_handler(exception_type = Exception, task = 'platform')
        fail = True
    
    # Check that GAM resides in the directory
    if os.path.isfile(f'{location}') == False:
        err_handler(exception_type = Exception, task = 'gam_installed',)
        fail = True
=======
    assert(
        os.path.isfile(GAM)
    ), err_handler(exception_type = Exception, task = 'gam_installed')

    # Check that oauth2.txt file with credentials exists
    assert(
        os.path.isfile(GAMDIR + 'oauth2.txt')
    ), err_handler(exception_type = Exception, task = 'gam_installed')

    # Check that Oblivio directory exists, otherwise, create it
    if os.path.isdir(OBLIVIODIR) == False:
        os.mkdir(OBLIVIODIR)
    
    # Get user ID to use when calling GAM for file uploads to Google
    user_id = get_user_id()

    # Datestring instance with today's date and 10 days ago
    dateobj = Datestring()
    
    # Fetch lists of chrome devices from G Suite with GAM
    active_crosdev = get_cros(
        dateobj.present, dateobj.past, domain_wide = False
    )

    all_crosdev = get_cros(
        dateobj.present, dateobj.past, domain_wide = True
    )

    # Calculate the inactive devices by subtracting the active ones
    if len(active_crosdev) != len(all_crosdev):
        inactive_crosdev = compute_diff(active_crosdev, all_crosdev)
        # Instanciate object to upload data to Google Drive
        oblivio = InactiveDevicesCsv(
            inactive_crosdev, OBLIVIODIR, GAM, GAMDIR, user_id, dateobj
        )
        # Create csv locally containing all inactive devices
        oblivio.create_csv()
        # Upload csv
        oblivio.upload_csv()

    else:
        inactive_crosdev = None
        print(
            'Oblivio: No inactive devices found for the current timespan.'
        )


def get_user_id():
    ''' Parse oauth2.txt file that GAM uses and fetch the google 
    username to be used when calling GAM to upload the Oblivio.csv 
    file '''
    
    count = 0
>>>>>>> 620da4a9805a947ad72a1123aac081e62ccfa2ff
    
    # Check that oauth2.txt file with credentials exists
    if os.path.isfile(f'{location}\\oauth2.txt') == False:
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
        user_id = get_user_id(f'{ARGS.gampath}\\oauth2.txt')
    else:
        user_id = ARGS.user

    # If timedelda is not set by commandline argument, use default
    if not ARGS.timedelta:
        __delta = 10
    else:
        __delta = ARGS.timedelta

    # Create instance of Inventory object and set properties
    oblivio = Inventory(delta = __delta, gam_path = f'{ARGS.gampath}')

<<<<<<< HEAD
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
=======
    if domain_wide == True:
        gam_command = [
            GAM, 'print', 'cros', 'orderby', 'lastsync', 'status',
            'fields', 'status', 'lastsync', 'serialnumber', 'OU'
        ]
    else:
        gam_command = [
            GAM, 'print', 'cros', 'query', 
            'sync:' + str(then + '..' + today), 
            'fields', 'status', 'lastsync', 'serialnumber', 'orderby', 
            'lastsync', 'status', 'serialnumber', 'OU'
        ]

    try:
        # Call GAM and run command depending on 'domain wide' or not
        gam_call = subprocess.run(gam_command, capture_output = True)
        gam_output = str(gam_call)
        # Format each device in the GAM output with removed clutter
        gam_output = gam_output.split('\\n')

    except:
        err_handler(exception_type = RuntimeError, task = 'gam_call')

    else:
        # # Comprehend a list containing all devices in the GAM output
        for i in gam_output:
            if not 'stderr' in i and not 'print' in i:
                devices_arr.append(i)

        return devices_arr


def compute_diff(active_devices, all_devices):
    ''' Calculate the inactive devices in the given time frame.
    List is made containing only the devices not occurring in 
    both all and active devices. This yields the devices not used
    in the given time frame. '''
    inactive_devices = [
        i for i in all_devices if not i in active_devices and not 'DEPROVISIONED' in i
    ]

    if len(inactive_devices):
        # Delete last entry which is always empty
        del inactive_devices[-1]
        # Keep only last sync date and serialnumber for each index
        for i in range(len(inactive_devices)):
            inactive_devices[i] = inactive_devices[i].split(',')
            inactive_devices[i] = inactive_devices[i][2:]
        
        # Add header tag at the beginning of the list
        _phrase = ['Last used', 'Serialnumber', 'Organizational unit']
        inactive_devices.insert(0, _phrase)
        return inactive_devices
    else:
        return None
   
if __name__ == '__main__':
    main()
>>>>>>> 620da4a9805a947ad72a1123aac081e62ccfa2ff
