from datetime import datetime, timedelta 
import subprocess

dateobject = datetime.today()



def get_today(dateobj):
	today = dateobject.strftime('%Y-%m-%d')
	if len(today) == 10:
		return today
	else:
		err_handler('Today\'s date error - Not defined or string incomplete')


def get_yesterday(dateobj):
	_tendaysago = dateobject + timedelta(days=(-10))
	tendaysago = _tendaysago.strftime('%Y-%m-%d')
	return tendaysago


def get_cros(domain_wide=False, today, yesterday):
	'''Ask GAM to fetch all cros devices in to set() and return it.
	TODO: Date time variables for command towards GAM
	'''
	if domain_wide == True:
		gam_command = (
			"gam print cros orderby lastsync "
			"fields lastsync, serialnumber")
	else:
		gam_command = (
			"gam print cros query sync:"+tendaysago_str+'..'+todaydate +
			"fields lastsync, serialnumber orderby" 
			"lastsync, serialnumber")
	_out = subprocess.Popen(gam_command, stdout=subprocess.PIPE)
	devices = str(_out.communicate()).split('\\r\\n')
	devices_arr = [i for i in devices if not 'None' in x and not 'deviceId' in x]
	return device_arr


def err_handler(Error=None):
	pass


# debug: get_cros()