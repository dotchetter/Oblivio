

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools

SCOPES = 'https://googleapis.com/auth/admin.directory.user'

def main():

	store = file.Storage('token.json')
	creds = store.get()
	if not creds or creds.invalid:
		flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
		creds = tools.run_flow(flow, store)

	service = build('admin', 'directory_v1', http=creds.authorize(Http()))

	print('Getting all users in the domain')
	results = service.users().list(customer='KSAB', MaxResults=99999,
		orderBy='email').execute()
	users = result.get('users', [])

	if not users:
		print('No users in the domain')
	else:
		print('Users:')
		for i in users:
			print(u'{0} ({1}'.format(i['primaryEmail'],user['name']['fullName']))


# if __name__ == '__main__':
# 	main()

