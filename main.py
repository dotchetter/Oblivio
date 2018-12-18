
import subprocess
import datetime


def get_cros(domainwide=False, todydate, datescope):
	'''Ask GAM to fetch all cros devices in to set() and return it.
	TODO: Date time variables for command towards GAM
	'''
	if domainwide == True:
		gam_command = (
			"gam print cros orderby lastsync "
			"fields lastsync, serialnumber")
	else:
		gam_command = (
			"gam print cros query sync:" + tendaysago_str..today + # non-declared variables, pseudo
			"fields lastsync, serialnumber orderby" 
			"lastsync, serialnumber")

	_out = subprocess.Popen(gam_command, stdout=subprocess.PIPE)
	devices = str(_out.communicate()).split('\\r\\n')
	device_arr = [x for x in devices if not 'None' in x and not 'deviceId' in x]
	return device_arr

def get_synced(days=None)
	gam_command = (
		"gam print cros orderby lastsync "
		"fields lastsync, serialnumber")

	_out = subprocess

#debugging only:
get_cros()