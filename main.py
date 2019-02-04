import os
import sys
import subprocess
from datestring import Datestring

def main():
    # Verify platform compatibility
    assert (
        'darwin' in sys.platform
    ), err_handler(exception_type = 'Exception', task = 'platform')
    
    # Date object with today's date (self.present) and 10 days ago (self.past)
    dateobj = Datestring()
    
    # Call functions to fetch lists of chrome devices from G Suite with GAM
    active_crosdev = get_cros(dateobj.present, dateobj.past, domain_wide = False)
    all_crosdev = get_cros(dateobj.present, dateobj.past, domain_wide = True)

    # Calculate the inactive devices by subtracting the active ones
    inactive_crosdev = compute_diff(active_crosdev, all_crosdev)

    # DEBUG:
    if (len(inactive_crosdev)):
        print('Oblivio found', len(inactive_crosdev), 'inactive devices: ', end = '\n')
        for i in inactive_crosdev:
            print(i)

def get_cros(today, then, domain_wide = False):
    ''' Call GAM and fetch Chrome OS devices from the domain. domain_wide
    or not will determine if all chrome os devices are fetched or only the active
    ones in the given time frame. 'today' and 'then' variables are date objects
    in string format given as a time frame for the device queries.'''

    if domain_wide == True:

        gam_command = [
            'gam', 'print', 'cros', 'orderby', 'lastsync', 
            'fields', 'lastsync,', 'serialnumber'
        ]

    else:
        gam_command = [
            'gam', 'print', 'cros', 'query', 
            'sync:' + str(then + '..' + today), 
            'fields', 'lastsync,', 'serialnumber', 
            'orderby', 'lastsync', 'serialnumber'
        ]
    
    try:

        # Call GAM and run command depending on the query (domain wide or not)
        gam_call = subprocess.run(gam_command, capture_output = True)
        gam_output = str(gam_call)
        # Format each device in the GAM output with removed clutter
        gam_output = gam_output.split('\\r\\n')

    except:
        err_handler(exception_type = RuntimeError, task = 'gam')

    else:

        # Comprehend a list containing all devices in the GAM output string
        devices_arr = [i for i in gam_output]

        return devices_arr

def compute_diff(active_devices, all_devices):
    ''' Calculate the inactive devices in the given time frame.
    List is made containing only the devices not occurring in both all and active
    devices. This yields the devices not used in the given time frame. '''
    inactive_devices = [
        i for i in all_devices if not i in active_devices
    ]
    
    # Keep only last sync date and serialnumber for each index in the list
    if len(inactive_devices):
        for i in range(len(inactive_devices)):
            inactive_devices[i] = inactive_devices[i].split(',')
            inactive_devices[i] = inactive_devices[i][1:]
        
        # Remove indexes in the list which are empty or otherwise not interesting
        for i in range(2):
            del inactive_devices[-1]
        del inactive_devices[0]

        return inactive_devices
    else:
        return None
   
def err_handler(exception_type = None, task = None):
    ''' Handle errors on exception and stop execution '''
    
    if task == 'gam':
        msg = 'Could not proceed; GAM is not responding, is it installed?\n'
    elif task == 'platform':

        msg = 'This version of Oblivio is designed to run on Windows only.'


    raise exception_type(msg)
    sys.exit()
 
if __name__ == '__main__':
    main()