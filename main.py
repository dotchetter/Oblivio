
from datetime import datetime, timedelta 
import subprocess

dateobject = datetime.today()

def main():
    today = get_today(dateobject)
    then = get_then(dateobject)
    all_crosdev = get_cros(today, then, domain_wide = True)
    active_crosdev = get_cros(today, then, domain_wide = False)
    print(active_crosdev)


def compute_diff(active_devlist, all_devlist):
    ''' Fetch devices from G Suite and compare active devices in G suite versus 
    all devices to computeinactive devices within given time scope '''
    pass


def get_today(dateobj):
    ''' Return today's date as string, format yyyy-mm-dd '''

    date = dateobject.strftime('%Y-%m-%d')
    if len(date) == 10:
        return date
    else:
        err_handler('Today\'s date error')


def get_then(dateobj):
    ''' Return a date for (today minus 10 days) as string, format yyyy-mm-dd '''

    _tendaysago = dateobject + timedelta(days = ( - 10))
    tendaysago = _tendaysago.strftime('%Y-%m-%d')
    if len(tendaysago) == 10:
        return tendaysago
    else:
        err_handler('Old date not defined')


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
    _out = subprocess.Popen(gam_command, stdout=subprocess.PIPE)
    devices = str(_out.communicate()).split('\\r\\n')
    devices_arr = [i for i in devices if not 'None' in i and not 'deviceId' in i]
    
    if len(devices_arr):
        for i in devices_arr:
            i.split()
        return devices_arr
    else:
        # Move up
        return('No active devices between ' + str(then) + ' and ' + str(today))



def err_handler(Error=None):
    pass

# debug: 