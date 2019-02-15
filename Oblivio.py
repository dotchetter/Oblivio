
import subprocess
import csv
from datetime import *

class Datestring():
    from datetime import datetime
    '''Date object returned in string format. self.present represents 
    today,self.past represents ten days ago, computed from today's 
    date object.'''

    def __init__(self, present = None, past = None):
        _dateobj = datetime.today()
        _pastobj = _dateobj + timedelta(days = (-10))
        self.past = _pastobj.strftime('%Y-%m-%d')
        self.present = _dateobj.strftime('%Y-%m-%d')

class InactiveDevicesCsv:
    ''' Create an object that holds a list of inactive devices
    and format them in a CSV format. Methods for creating the CSV 
    file locally, and uploading the CSV to G Suite using GAM as 
    separate process.'''
    
    def __init__(self, cros_list, oblivio_path, gam, gam_path, user_id):
        self.cros_list = cros_list
        self.oblivio_path = oblivio_path
        self.gam = gam
        self.gam_path = gam_path
        self.csv = (self.oblivio_path + '/Oblivio.csv')
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
            'drivefile', 'localfile', self.csv, 'convert'
        ]

        try:
            _gam_call = subprocess.run(_gam_command, capture_output = True)
        except:
            err_handler(exception_type = RuntimeError, task = 'csv_upload')
        else:
            return 'Upload complete'

def err_handler(exception_type = None, task = None):
    ''' Handle errors on exception and stop execution '''
    # DEBUG: 
    print(exception_type, task)
    if task == 'gam_call':
        msg = 'Oblivio: Could not proceed; GAM is not responding.'
    elif task == 'platform':
        msg = (
        'Oblivio: This version of Oblivio is designed to run ' + 
        'on MacOS only. Download the right version for your OS.'
        ) 
    elif task == 'gam_installed':
        msg = 'Oblivio: GAM was not found to be installed. Check path.'
    elif task == 'get_user_id':
        msg = ('Oblivio: An error occured while parsing the oauth2.txt file for ' + 
        'G suite username, username was not found in expected key.'
        )
    elif task == 'csv_creation':
        msg = 'Oblivio: An error occured while creating the CSV file.'
    elif task == 'csv_upload':
        msg = 'Oblivio: An error occured while using GAM to upload the csv file.'

    raise exception_type(msg)
    sys.exit()
