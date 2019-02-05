
import os
import sys
import subprocess
from datestring import Datestring

# Set GAM as installed in default directory in user's $home.
GAM = os.getenv("HOME") + '/bin/gam/gam'

def main():
    
    # Verify platform compatibility
    assert (
        'darwin' in sys.platform
    ), err_handler(exception_type = 'Exception', task = 'platform')
    
    # Check that GAM resides in the presumed directory
    assert (
        os.path.isfile(GAM)
    ), err_handler(exception_type = 'Exception', task = 'gam_installed')

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
    else:
        inactive_crosdev = None
        print(
            'Oblivio: No inactive devices found for the current timespan.'
        )

    # Alpha prior to Google Sheet upload:
    if inactive_crosdev != None:
        print(
            'Oblivio: I found', len(inactive_crosdev), 
            'inactive devices: ', end = '\n'
        )
        
        for i in inactive_crosdev:
            print(i, end = '\n')

def get_cros(today, then, domain_wide = False):
    ''' Call GAM and fetch Chrome OS devices from the domain. domain_wide
    or not will determine if all chrome os devices are fetched or only 
    the active ones in the given time frame. 'today' and 'then' 
    variables are date objects in string format given as a time frame 
    for the device queries.'''

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
        gam_output = gam_output.split('\\n')

    except:
        err_handler(exception_type = RuntimeError, task = 'gam_call')

    else:

        # # Comprehend a list containing all devices in the GAM output
        # devices_arr = [i for i in gam_output]

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
        
        return inactive_devices
    else:
        return None
   
def err_handler(exception_type = None, task = None):
    ''' Handle errors on exception and stop execution '''
    
    if task == 'gam_call':
        msg = 'Oblivio: Could not proceed; GAM is not responding.'
    elif task == 'platform':
        msg = (
        'Oblivio: This version of Oblivio is designed to run ' + 
        'on MacOS only.vDownload the right version for your OS.'
    ) 
    elif task == 'gam_installed':
        msg = 'Oblivio: GAM was not found to be installed. Check path.'

    raise exception_type(msg)
    sys.exit()
 
if __name__ == '__main__':
    main()