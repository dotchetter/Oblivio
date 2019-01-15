from datetime import datetime, timedelta

class Datestring:
    ''' Date object returned in string format. self.present represents today,
        self.past represents ten days ago, computed from today's date object.'''
    def __init__(self, present = None, past = None):
        __dateobj = datetime.today()
        __pastobj = __dateobj + timedelta(days = ( -10))
        self.past = __pastobj.strftime('%Y-%m-%d')
        self.present = __dateobj.strftime('%Y-%m-%d')