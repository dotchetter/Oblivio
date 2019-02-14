
import os
import sys
import json
import subprocess
from Oblivio import *

# Set GAM as installed in default directory in user's $home.
GAM = os.getenv("SYSTEMDRIVE") + '\\gam\\gam.exe'
# Set GAMDIR as the directory where GAM is installed per default
GAMDIR = GAM.strip('gam.exe')
# Set Oblivio dir inside the GAM dir
OBLIVIODIR = GAMDIR + 'Oblivio'

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
            inactive_crosdev, OBLIVIODIR, GAM, GAMDIR, user_id
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

    # NOTE: Debug
    return inactive_crosdev


def get_user_id():
    ''' Parse oauth2.txt file that GAM uses and fetch the google 
    username to be used when calling GAM to upload the Oblivio.csv 
    file '''
    
    count = 0
    
    try:
        with open(GAMDIR + 'oauth2.txt') as _file:
            _user_id = json.load(_file)
            _user_id = _user_id.get('id_token')
            _user_id = _user_id.get('email')
    except:
        err_handler(exception_type = RuntimeError, task = 'get_user_id')
    else:
        # Strip the user name from domain to minimize leakage risk
        for i in _user_id:
            count += 1
            if i == '@':
                index = count

        _user_id = _user_id[0:index - 1]
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
            GAM, 'print', 'cros', 'orderby', 'lastsync', 
            'fields', 'lastsync,', 'serialnumber'
        ]

    else:
        gam_command = [
            GAM, 'print', 'cros', 'query', 
            'sync:' + str(then + '..' + today), 
            'fields', 'lastsync,', 'serialnumber', 
            'orderby', 'lastsync', 'serialnumber'
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
        i for i in all_devices if not i in active_devices
    ]

    if len(inactive_devices):
        # Delete last entry which is always empty
        del inactive_devices[-1]
        # Keep only last sync date and serialnumber for each index
        for i in range(len(inactive_devices)):
            inactive_devices[i] = inactive_devices[i].split(',')
            inactive_devices[i] = inactive_devices[i][1:]

        # Add header tag at the beginning of the list
        _phrase = ['Last used', 'Serialnumber']
        inactive_devices.insert(0, _phrase)
                
        return inactive_devices
    else:
        return None
   
if __name__ == '__main__':
    main()