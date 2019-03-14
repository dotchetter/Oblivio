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
import subprocess
import csv
from datetime import datetime, timedelta

class Datestring():
    ''' Date object returned in string format. 

    Contain fields which represents the day of today's date
    in yyyy-mm-dd format, and a date in the same format minus
    the delta being given. For instance, a delta of 10 on 
    2018-01-30 gives 2018-01-20. '''

    def __init__(self, delta = 10):
        self._delta = delta
        self._dateobj = datetime.today()
        self._pastobj = self._dateobj + timedelta(days = ( - self._delta))
        self.past = self._pastobj.strftime('%Y-%m-%d')
        self.present = self._dateobj.strftime('%Y-%m-%d')

class Inventory(Datestring):
    ''' Object containing inactive devices, fetched from
    GAM with communicating commands to GAM via SubProcess

    Commands are passed to the CLI application GAM, to 
    fetch devices from the G Suite domain. Two tuples with
    a series of commands are passed to GAM and the output 
    is then parsed. The instance of this class will have 
    fields that contain the inactive devices, all devices,
    and their status (deprovisioned, active, disabled). 

    Attributes:
    
    all_devices --      All devices in the domain in a List
    
    active_devices --   All devices in the domain that have been 
                        synced within the given timeframe
    
    inactive_devices -- Subtracted devices from all_devices that were 
                        not found in active_devices. This leaves them
                        as inactive, that is, in the domain but not 
                        used in the provided timeframe.
    
    provisioned --      Devices in inactive_devices that are set as 
                        ACTIVE, meaning provisioned in the domain.
    
    deprovisioned --    Devices in inactive_devices that are set as 
                        DEPROVISIONED
    
    disabled --         Devices in inactive_devices that are set as
                        DISABLED '''

    def __init__(self, delta = 10, gam_path = None):
        
        # Instanciate Datestring Object
        Datestring.__init__(self, delta = int(delta))
        self._gam_path = gam_path
        # Set properties
        self.all_devices
        self.active_devices
        self.inactive_devices
        self.provisioned
        self.deprovisioned
        self.disabled

    @property
    def all_devices(self):
        ''' Pass arguments to GAM and redirect stdout to 
        parse the output of devices that are recieved. 
        Get all cros devices in the domain in tuple. '''

        # Fetch all crome os devices in the domain
        _cmd = (self._gam_path, 'print',
                'cros', 'orderby',  
                'lastsync', 'status',
                'fields', 'status', 
                'lastsync', 'serialnumber',
                'OU'
        )

        # Call method to pass arguments to GAM
        # Set the property to the returned list object as a set()
        self._all_devices = self.init_gam(_cmd)
            
    @property
    def active_devices(self):
        ''' Pass arguments to GAM and redirect stdout 
        to parse the output of devices that are recieved. 
        Get all cros devices in the domain in tuple. '''

        # Fetch only active crome os devices in the domain
        _cmd = (self._gam_path, 'print',
                'cros', 'query',
                'sync:' + str(self.past + '..' + self.present), 
                'fields', 'status',
                'lastsync', 'serialnumber',
                'orderby', 'lastsync',
                'status', 'serialnumber',
                'OU'
        )

        # Call method to pass arguments to GAM
        # Set the property to the returned list object as List
        self._active_devices = self.init_gam(_cmd)

    @property
    def inactive_devices(self):
        ''' Field containing a subtraction of all active
        devices from all_devices, leaving only the inactive 
        devices. '''

        self._inactive_devices = [
            i for i in self._all_devices if not i in self._active_devices
        ]

    @property
    def provisioned(self):
        ''' Field containing devices that were found to be
        inactive and are active in the domain '''

        # Comprehend list with only the provisioned "inactive devices"
        self._provisioned = [
            i for i in self._inactive_devices if i[0] == 'ACTIVE'
        ]

    @property
    def deprovisioned(self):
        ''' Field containing devices that were found to be
        inactive and are deprovisioned in the domain '''

        # Comprehend list with only the deprovisioned inactive devices
        self._deprovisioned = [
            i for i in self._inactive_devices if i[0] == 'DEPROVISIONED'
        ]

    @property
    def disabled(self):
        ''' Field containing devices that were found to be
        inactive and are disabled in the domain '''

        # Comprehend list with only the disabled inactive devices
        self._disabled = [
            i for i in self._inactive_devices if i[0] == 'DISABLED'
        ]

    def init_gam(self, cmdlist):
        ''' Process a series of commands passed. 
        A list object with nested lists is returned with the 
        devices. The first index in the parent list is removed,
        as it contains only header data. For each sublist, the 
        first index is removed as it contains unwanted 
        DeviceID string. '''

        # Initiate subprocess and process commands
        try:
            _gam_call = subprocess.run(cmdlist, capture_output = True)
            _gam_output = str(_gam_call)
            # Format each device in the GAM output with removed trails
            _gam_output = _gam_output.split('\\r\\n')
        except Exception as e:
            raise Exception(e)
        else:
            __devicelist = [
                i for i in _gam_output if not 'CompletedProcess' in i and not 'CrOS' in i
            ]
            # Remove trailing parenthesis, last index in the list
            __devicelist.pop(-1)
            # Remove Device ID string from each device
            for index in range(len(__devicelist)):
                __devicelist[index] = __devicelist[index].split(',')
                # Removing device ID strings
                __devicelist[index] = __devicelist[index][1:]
            return __devicelist

class LocalFileCreator(Inventory):
    ''' Create an object that holds a list of inactive devices
    and format them in a CSV format. Methods for creating the CSV 
    file locally, and uploading the CSV to G Suite using GAM as 
    separate process.'''
    
    def __init__(self, cros_list, oblivio_path, gam, gam_path, user_id, dateobject):
        self.cros_list = cros_list
        self.oblivio_path = oblivio_path
        self.gam = gam
        self.gam_path = gam_path
        self.csv = ("{}{} {}{}".format(
            self.oblivio_path,'\\Oblivio', dateobject.present, '.csv')
        )
        self.user_id = user_id
    
    def create_csv(self):
        ''' Build CSV file from list object. '''
        try:
            with open(self.csv,'w', newline = '') as outfile:
                writer = csv.writer(outfile)
                writer.writerows(self.cros_list)
                outfile.close()
        except:
            err_handler(exception_type = RuntimeError, task = 'csv_creation')

    def upload_csv(self):
        ''' Generate list with GAM arguments to upload csv to Google Drive '''
        _gam_command = [
            self.gam, 'user', self.user_id,'add', 
            'drivefile', 'localfile', self.csv, 'convert', 'parentname', 'Oblivio'
        ]

        try:
            # Call GAM to upload the CSV to Google 
            _gam_call = subprocess.run(_gam_command, capture_output = True)
            if 'unauthorized_client' in str(_gam_call):        
                err_handler(exception_type = ChildProcessError, task = 'not_authorized')
        except:
            err_handler(exception_type = ChildProcessError, task = 'csv_upload')
        else:
            return 'Upload complete'

def err_handler(exception_type = None, task = None):
    ''' Handle errors on exception and stop execution '''

    if task == 'gam_call':
        msg = 'Oblivio: Could not proceed; GAM is not responding.'
    elif task == 'platform':
        msg = (
        'Oblivio: This version of Oblivio is designed to run ' + 
        'on Windows only. Download the right version for your OS.'
        ) 
    elif task == 'gam_installed':
        msg = 'Oblivio: GAM was not found to be installed. Check path.'
    elif task == 'oauthfile':
        msg = ('Oblivio: No user was given, and I was unable to parse ' +
            'the file containing user configured with GAM. Please use the user switch.'
        )
    elif task == 'get_user_id':
        msg = ('Oblivio: An error occured while parsing the oauth2.txt file for ' + 
            'G suite username, username was not found in expected key.'
        )
    elif task == 'not_authorized':
        msg = 'Oblivio: GAM is not authorized to upload files with this project.'
    elif task == 'csv_creation':
        msg = 'Oblivio: An error occured while creating the CSV file.'
    elif task == 'csv_upload':
        msg = 'Oblivio: An error occured while using GAM to upload the csv file.'

    raise exception_type(msg)
    sys.exit()
