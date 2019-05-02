#!/usr/bin/env/python3
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

from datetime import datetime
from Oblivio import *

# Add commandline parameters when running Oblivio
argument_parser = argparse.ArgumentParser(
    description = '''Oblivio v.1.2 by Simon Olofsson. See separate
                    technical manual on extensive help how to use Oblivio. 
                    Example minimal command: "Oblivio <gampath> <outpath>  
                    <user> <optionals> '''
)

# Add help strings to tuple
help_strings = (
    'Directory where the GAM binary is located. '
    'Example: "~/GAM"',
    
    'Where Oblivio will store outputfiles. '
    'Example: "~/GAM/OblivioOutputFiles"',
    
    'Email adress prefix (or the complete adress) for the account where '
    'Oblivio will upload files to. Example: "captain.kirk"',
    
    'Use this switch if you wish for the output .xlsx file being removed '
    'automatically when Oblivio is done uploading it to Google Drive.',

    'Number of days unused for a device to be included. Default is 10. '
    'Example: "-timedelta 100"',

    'Get Oblivio output in the shell. No local file is created or uploaded.'
)

# Add commandline switches
argument_parser.add_argument('gampath', help = help_strings[0])
argument_parser.add_argument('outpath', help = help_strings[1])
argument_parser.add_argument('user', help = help_strings[2])
argument_parser.add_argument('-nofile', action = 'store_true', help = help_strings[3])
argument_parser.add_argument('-timedelta', help = help_strings[4])
argument_parser.add_argument('-verbose', action = 'store_true', help = help_strings[5])

# Parse all arguments given in to list object
ARGS = argument_parser.parse_args()

# Timestamp in UNIX time for the beginning of execution
start = datetime.now().timestamp()

def verify_prereq(location):
    ''' Verify prerequisites to make sure preconditions are met '''
    check = True
    
    # Verify platform compatibility
    if not 'linux' in sys.platform:
        raise Exception('This version of Oblivio is designed for Linux.')
        check = False
    # Check that GAM resides in the directory
    elif os.path.isfile(f'{location}/gam') == False:
        raise Exception('GAM was not found in the specified directory.')
        check = False   
    return check

if __name__ == '__main__':
    
    # Verify that GAM and Oauth file is found
    ready = verify_prereq(ARGS.gampath)
    if ready == False:
        sys.exit()

    # Set the user ID to the given string in argument
    user_id = ARGS.user

    # Set timedelta to argument value, otherwise use 10 as default
    if ARGS.timedelta:
        __delta = ARGS.timedelta
    else:
        __delta = 10

    print('\n','Running GAM with Oblivio magic. This will take some time, ','\n',
        'as we fetch every single Chrome OS device in your entire domain.','\n',
        'Normal runtime: < 10 minutes for 25000 CROS devices.'
    )

    # Create instance of Inventory object and set properties
    oblivio = Inventory(delta = __delta, gam_path = f'{ARGS.gampath}/gam')

    # Unless '-verbose' parameter given, create folder and output file
    if not ARGS.verbose == True:
        file = Localfile(oblivio, ARGS.outpath, user_id)

    # If commandline argument '-verbose' is given, print output to 
    # screen and do not upload or create any files on the system.
if ARGS.verbose:
    _dates = f'{oblivio.past} - {oblivio.present}'

    print('\n',f'UNUSED DEVICES BETWEEN {_dates}: {len(oblivio.inactive_devices)}', '\n')
    for i in oblivio.inactive_devices:
        print(i, end = '\n')
    
    print('\n','.. OF WHICH UNUSED ARE PROVISIONED DEVICES:', len(oblivio.provisioned), '\n')
    for i in oblivio.provisioned:
        print(i, end = '\n')
    
    print('\n','.. OF WHICH UNUSED ARE DEPROVISIONED DEVICES:', len(oblivio.deprovisioned), '\n')
    for i in oblivio.deprovisioned:
        print(i, end = '\n')
    
    print('\n','.. OF WHICH UNUSED ARE DISABLED DEVICES:', len(oblivio.disabled), '\n')
    for i in oblivio.disabled:
        print(i, end = '\n')
else:
    # If Verbose switch is not used, create the local file and upload it
    file_exists = file.create()
    if file_exists == True:
        upload_successful = file.upload()
        if upload_successful != True:
            raise Exception('An error with uploading the file halted the program.')

    # If 'nofile' parameter is specified, remove the inventory file
    if ARGS.nofile:
        file.delete()
    fin = datetime.now().timestamp()
    print(f'Finished in {(fin - start)} seconds.')