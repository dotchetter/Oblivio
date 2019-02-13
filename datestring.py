
from datetime import datetime, timedelta
import csv

class Datestring:
    ''' Date object returned in string format. self.present represents 
    today,self.past represents ten days ago, computed from today's 
    date object.'''
   
    def __init__(self, present = None, past = None):
        __dateobj = datetime.today()
        __pastobj = __dateobj + timedelta(days = (-10))
        self.past = __pastobj.strftime('%Y-%m-%d')
        self.present = __dateobj.strftime('%Y-%m-%d')

class InactiveDevicesCsv:
	''' Create an object that holds a list of inactive devices
	and format them in a CSV format. Upload CSV to G Suite. '''
	
	def __init__(self, cros_list, home_path, gam_path):
		self.cros_list = cros_list
		self.home_path = home_path
		self.gam_path = gam_path
		self.csv = (self.home_path + '\\Oblivio.csv')
	
	def create_csv(cls, cros_list):
		@classmethod
		try:
			with open(self.csv,'w', newline = '') as outfile:
	     		writer = csv.writer(cros_list)
	     		writer.writerows(cros_list)
	    except:
	    	# Raise an error here
		
	def upload_csv(cls):
		@classmethod
		
		# List with GAM arguments to upload csv to Google Drive
		__gam_command = [
			self.gam_path, 'gam user',
			'simon.olofsson@gedu.demo.caperiodemo.se',
			'add', 'drivefile', 'localfile', self.csv
		]

		try:
			__gam_call = subprocess.run(__gam_command, shell = False)
		except:
			# Raise an error here
		else:
			return 'Upload complete'





# Command to upload sheet to drive
# gam user 'simon.olofsson@gedu.demo.caperiodemo.se' add 
# drivefile localfile 'C:\users\siolo001.caperio\desktop\test.csv'