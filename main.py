
from datestring import Datestring
import subprocess


def main():
    # Create date object with today's date (self.present) and 10 days ago (self.past)
    dateobj = Datestring()
    # Call functions to fetch lists of chrome devices from G Suite with GAM
    active_crosdev = get_cros(dateobj.present, dateobj.past, domain_wide = False)
    all_crosdev = get_cros(dateobj.present, dateobj.past, domain_wide = True)
    # Calculate the inactive devices by subtracting the active from all
    inactive_crosdev = compute_diff(active_crosdev, all_crosdev)


def compute_diff(active_devices, all_devices):
    ''' Fetch devices from G Suite and compare active devices in G suite versus 
    all devices to compute inactive devices within given time scope '''
    inactive_devices = [i for i in all_devices if not i in active_devices]
    
    # DEBUG:
    print(len(inactive_devices), 'inactive devices found...')
    print(inactive_devices)

def get_cros(today, then, domain_wide = False):
    ''' Ask GAM to fetch all cros devices in to set() and return it.
    TODO: Date time variables for command towards GAM. Arguments tell whether
    to do a domain-wide query or to fetch only active. today, then, represent
    date strings for GAM query command. '''

    if domain_wide == True:
        gam_command = ('gam print cros orderby lastsync '
                        'fields lastsync, serialnumber')
    else:
        gam_command = ("gam print cros query sync:" + then + '..' + today 
                        + " fields lastsync, serialnumber orderby lastsync serialnumber")
    
    # Call GAM and run command depending on the query (domain wide or not)
    gam_call = subprocess.Popen(gam_command, stdout=subprocess.PIPE)
    devices = str(gam_call.communicate()).split('\\r\\n')

    # Create a list containing only the devices, not header in the query
    devices_arr = [i for i in devices if not 'None' in i and not 'deviceId' in i]
    
    if len(devices_arr):
        for i in devices_arr:
            i.split()
        return devices_arr
    else:
        # Move up
        return('No active devices between ' + str(then) + ' and ' + str(today))



def err_handler(Error = None):
    pass

# debug: 

if __name__ == '__main__':
    main()