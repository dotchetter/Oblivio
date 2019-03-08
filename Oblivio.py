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
    fetch devices from the G Suite domain. A tuple of queries
    consisting two tuples with a series of commands are passed
    to GAM and the output is then parsed. The instance of this 
    class will have fields that contain the inactive devices, 
    all devices, and their status (deprovisioned, provisioned, 
    disabled). '''

    def __init__(self, delta = 10, gam_path = None):
        
        # Instanciate Datestring Object
        Datestring.__init__(self, delta = delta)
        self._gam_path = gam_path

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
        return set(self.init_gam(_cmd))
    
    @property
    def active_devices(self):
        return self._active_devices
    
    @active_devices.setter
    def active_devices(self, active_devices):
        ''' Pass arguments to GAM and redirect stdout 
        to parse the output of devices that are recieved. 
        Get all cros devices in the domain in tuple. '''

        # Fetch only active crome os devices in the domain
        _cmd = (gam_path, 'print',
                'cros', 'query',
                'sync:' + str(Datestring.preset + '..' + Datestring.past), 
                'fields', 'status',
                'lastsync', 'serialnumber',
                'orderby', 'lastsync',
                'status', 'serialnumber',
                'OU'
        )

        # Call method to pass arguments to GAM
        # Set the property to the returned list object as a set()
        self._active_devices = set(self.init_gam(_cmd))

    @property
    def inactive_devices(self):
        return self._inactive_devices

    @inactive_devices.setter
    def inactive_devices(self, inactive_devices):
        ''' Field containing a subtraction of the active
        devices from all devices, leaving only the inactive 
        devices in a set() '''

        # Subract the active devices from all devices to get inactive
        self._inactive_devices = (self._all_devices - self._active_devices)

    @property
    def provisioned(self):
        return self._provisioned
    
    @provisioned.setter
    def provisioned(self, provisioned):
        ''' Field containing devices that were found to be
        inactive and are provisioned in the domain '''

        # Comprehend list with only the provisioned inactive devices
        __prov = [x for x in self._inactive_devices if 'provisioned' in i]
        self._provisioned = tuple(__prov)

    @property
    def deprovisioned(self):
        return self._deprovisioned
    
    @deprovisioned.setter
    def deprovisioned(self, deprovisioned):
        ''' Field containing devices that were found to be
        inactive and are deprovisioned in the domain '''

        # Comprehend list with only the deprovisioned inactive devices
        __deprov = [x for x in self._inactive_devices if 'deprovisioned' in i]
        self._deprovisioned = tuple(__deprov)

    @property
    def disabled(self):
        return self._disabled
    
    @disabled.setter
    def disabled(self, disabled):
        ''' Field containing devices that were found to be
        inactive and are disabled in the domain '''

        # Comprehend list with only the disabled inactive devices
        __prov = [x for x in self._inactive_devices if 'disabled' in i]
        self._disabled = tuple(__prov)

    def init_gam(self, cmdlist):
        '''Process a series of commands passed 
        to subprocess. Return tuple with output. '''

        # Initiate subprocess and process commands
        try:
            _gam_call = subprocess.run(cmdlist)
            _gam_output = str(_gam_call)
        
            # Format each device in the GAM output with removed trails
            _gam_output = _gam_output.split('\\r\\n')
        except Exception as e:
            raise Exception(e)
        else:
            # Comprehend a list with the output devices
            _output = [
                i for i in _gam_output if not 'print' in i and not 'stderr' in i
            ]


class LocalFileCreator():
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