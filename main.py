#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
MIT License

Copyright (c) 2018 

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
import subprocess
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
    'Remove the local file after upload.'
)

# Add commandline switches
argument_parser.add_argument('-example', help = help_strings[0])
argument_parser.add_argument('gampath', help = help_strings[1])
argument_parser.add_argument('outpath', help = help_strings[2])
argument_parser.add_argument('user', help = help_strings[3])
argument_parser.add_argument('upload', help = help_strings[4])
argument_parser.add_argument('-nofile', help = help_strings[5])

# Parse all arguments given in to list object
ARGS = argument_parser.parse_args()

def main():
    
    # Verify platform compatibility
    assert(
        'win32' in sys.platform
    ), err_handler(exception_type = Exception, task = 'platform')
    # Check that GAM resides in the presumed directory
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
    # Fetch list of active chrome devices from G Suite with GAM
    active_crosdev = get_cros(
        dateobj.present, dateobj.past, domain_wide = False
    )
    # Fetch list of all chrome devices from G Suite
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

def get_user_id(gamdir):                                # UNFINISHED
    ''' Return the username email for the authenticated 
    GAM user, stripped of the domain name to pass on to
    GAM. This is fetched if the 'default' parameter is
    given on the USER switch when Oblivio is run. '''
    try:
        with open(gamdir + 'oauth2.txt') as _file:
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
    
def get_cros(today, then, domain_wide = False):
    ''' Call GAM and fetch Chrome OS devices from the domain. 
    domain_wide or not will determine if all chrome os devices are 
    fetched or only the active ones in the given time frame. 
    'today' and 'then' variables are date objects in string format 
    given as a time frame for the device queries.'''

    devices_arr = []

    if domain_wide == True:
        gam_command = [
            GAM, 'print', 'cros', 'orderby',  'lastsync', 'status',
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
        gam_output = gam_output.split('\\r\\n')
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
   # main() DEBUG
   print(ARGS.user)