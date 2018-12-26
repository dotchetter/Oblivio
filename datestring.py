

class Datestring():

	def __init__(self, dateobject = None, past = None, present = None):

		self.dateobject = dateobject
		self.past = get_then(__dateobject)
		self.present = get_today(__dateobject)


	def get_today(dateobject):
	    ''' Return today's date as string, format yyyy-mm-dd '''	

	    today = dateobject.strftime('%Y-%m-%d')
	    if len(today) == 10:
	    	return today


	def get_then(dateobject):
	    ''' Return a date for (today minus 10 days) as string, format yyyy-mm-dd '''	

	    _tendaysago = dateobject + timedelta(days = ( - 50))
	    tendaysago = _tendaysago.strftime('%Y-%m-%d')
	    if len(tendaysago) == 10:
	    	return tendaysago