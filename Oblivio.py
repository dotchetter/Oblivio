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
import subprocess
import csv
import xlsxwriter
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
    and their status (deprovisioned, active, disabled). '''

    def __init__(self, delta = 10, gam_path = None):
        
        # Instanciate Datestring Object
        Datestring.__init__(self, delta = int(delta))
        self._gam_path = gam_path

        __all = self.__fetch_all_devices()
        __active = self.__fetch_active_devices()

        self._all_devices = __all
        self._active_devices = __active

    def __fetch_all_devices(self):
        ''' Pass arguments to GAM and redirect stdout to 
        parse the output of devices that are recieved. 
        Get all cros devices in the domain in tuple. '''

        # Fetch all crome os devices in the domain
        _cmd = (self._gam_path, 'print',
                'cros', 'orderby', 
                'status', 'fields',
                'status', 'serialnumber', 
                'OU'
        )

        # Call method to pass arguments to GAM
        # Set the property to the returned list object as a set()
        return self.init_gam(_cmd)

    def __fetch_active_devices(self):
        ''' Pass arguments to GAM and redirect stdout 
        to parse the output of devices that are recieved. 
        Get all cros devices in the domain in tuple. '''

        # Fetch only active crome os devices in the domain
        _cmd = (self._gam_path, 'print',
                'cros', 'query',
                'sync:' + str(self.past + '..' + self.present), 
                'fields', 'status',
                'serialnumber',
                'orderby', 'status', 
                'serialnumber', 'OU'
        )

        # Call method to pass arguments to GAM
        # Set the property to the returned list object as List
        return self.init_gam(_cmd)

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
            _gam_output = _gam_output.split('/r/n')
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

    @property
    def gam_path(self):
        return self._gam_path
    
    @property
    def all_devices(self):
        return self._all_devices

    @property
    def active_devices(self):
        return self._active_devices

    @property
    def inactive_devices(self):
        ''' Field containing a subtraction of all active
        devices from all_devices, leaving only the inactive 
        devices. '''

        # Comprehend list with all the inactive devices
        self._inactive_devices = [
            i for i in self._all_devices if not i in self._active_devices
        ]
        return self._inactive_devices

    @property
    def provisioned(self):
        ''' Field containing devices that were found to be
        inactive and are active in the domain '''

        # Comprehend list with only the provisioned "inactive devices"
        self._provisioned = [
            i for i in self._inactive_devices if i[0] == 'ACTIVE'
        ]
        return self._provisioned

    @property
    def deprovisioned(self):
        ''' Field containing devices that were found to be
        inactive and are deprovisioned in the domain '''

        # Comprehend list with only the deprovisioned inactive devices
        self._deprovisioned = [
            i for i in self._inactive_devices if i[0] == 'DEPROVISIONED'
        ]
        return self._deprovisioned

    @property
    def disabled(self):
        ''' Field containing devices that were found to be
        inactive and are disabled in the domain '''

        # Comprehend list with only the disabled inactive devices
        self._disabled = [
            i for i in self._inactive_devices if i[0] == 'DISABLED'
        ]
        return self._disabled


class Localfile():
    ''' Create an object that holds a list of inactive devices
    and format them in a CSV format. Methods for creating the CSV 
    file locally, and uploading the CSV to G Suite using GAM as 
    separate process.'''
    
    def __init__(self, inventoryobj, outpath, user_id):
       
        self._inventoryobj = inventoryobj
        # Filepath where to save the outputfile
        self._outpath = f'{outpath}/Oblivio {self._inventoryobj.present}.xlsx'
        # User ID when uploading file to Google Drive with GAM
        self._username = user_id

        # Assert the existence of the output directory, create
        # directory if non-existent
        if os.path.isdir(outpath) == False:
            os.mkdir(outpath)

    def create(self):
        ''' Build .xlsx file with one workbook per field.

        The data in inventoryobj related to deprovisioned
        devices, provisioned devices, all devices and 
        disabled devices all get their own workbook in the
        xlsx file. '''

        _DATESTR = f'{self._inventoryobj.past} - {self._inventoryobj.present}'
        INVENTORYINFO = (['Devices unused between:'], [_DATESTR])
        HEAD = (['Status'], ['Serialnumber'], ['OU'])

        try:
            wb = xlsxwriter.Workbook(self._outpath)
            
            # Worksheet containing all CROS devices that were unused
            ws_all = wb.add_worksheet('Unused devices')
            ws_all.set_column('A:D', 30)

            # Worksheet containing all CROS devices that are still provisioned
            ws_provisioned = wb.add_worksheet('Unused & Provisioned')
            ws_provisioned.set_column('A:D', 30)
            
            # Worksheet containing all CROS devices that are deprovisioned
            ws_deprovisioned = wb.add_worksheet('Unused & Deprovisioned')
            ws_deprovisioned.set_column('A:D', 30)
            
            # Worksheet containing all CROS devices that are disabled
            ws_disabled = wb.add_worksheet('Unused & Disabled')
            ws_disabled.set_column('A:C', 30)

            # Populate all inactive devices in the first sheet
            for index, string in enumerate(INVENTORYINFO):
                ws_all.write_row(0, index, string)
            for index, string in enumerate(HEAD):
                ws_all.write_row(1, index, string)
            for index, device in enumerate(self._inventoryobj.inactive_devices):
                ws_all.write_row((index + 2), 0, device)
            
            # Populate the 'Provisioned' sheet in the file
            for index, string in enumerate(HEAD):
                ws_provisioned.write_row(0, index, string)
            for index, device in enumerate(self._inventoryobj.provisioned):
                ws_provisioned.write_row((index + 1), 0, device)
            
            # Populate the 'Deprovisioned' sheet in the file
            for index, string in enumerate(HEAD):
                ws_deprovisioned.write_row(0, index, string)
            for index, device in enumerate(self._inventoryobj.deprovisioned):
                ws_deprovisioned.write_row((index + 1), 0, device)
            
            # Populate the 'Disabled' sheet in the file
            for index, string in enumerate(HEAD):
                ws_disabled.write_row(0, index, string)
            for index, device in enumerate(self._inventoryobj.disabled):
                ws_disabled.write_row((index + 1), 0, device)
            # Close file
            wb.close()
        except Exception as e:
            raise(e) 
        else:
            return True

    def upload(self):
        ''' Generate list with GAM arguments to upload csv to Google Drive '''
        _cmd = (
            self._inventoryobj.gam_path, 'user',
            self._username, 'add',
            'drivefile', 'localfile', 
            self._outpath, 'convert', 'parentname', 'oblivio'
        )
        try:
            # Call GAM to upload the CSV to Google 
            _gam_call = subprocess.run(_cmd, capture_output = True)
            if 'unauthorized_client' in str(_gam_call):        
                print('It seems as though you have not authorized GAM to '
                    'upload files. Ensure that your GAM project is '
                    'authorized with the Google Drive API.'
                )
        except Exception as e:
            raise(e)
            return False
        else:
            return True

    def delete(self):
        ''' Remove the file generated by the given instance. '''
        os.remove(self._outpath)