from flask import Flask, redirect, request
import requests

import oauth2client.client as oc
import gdata.gauth
import gdata.contacts.client


app = Flask(__name__)
flow = oc.flow_from_clientsecrets('/home/zopper/Desktop/client_secrets.json', scope='https://www.google.com/m8/feeds', redirect_uri='http://localhost:8080/gapicallback')
credentials = None
@app.route('/')
def hello_world():
	return redirect('/login')


@app.route('/login')
def login():
	auth_uri = flow.step1_get_authorize_url()
	return redirect(auth_uri)

@app.route('/gapicallback')
def check_login():
	code = request.args.get('code')
	if code is None:
		return 'invalid login'
	credentials = flow.step2_exchange(code)

	auth2token = gdata.gauth.OAuth2Token(client_id=credentials.client_id, client_secret=credentials.client_secret, scope='https://www.google.com/m8/feeds/contacts/default/full', access_token=credentials.access_token, refresh_token=credentials.refresh_token, user_agent='sites-test/1.0')
	client = gdata.contacts.client.ContactsClient()
	auth2token.authorize(client)

	query = gdata.contacts.client.ContactsQuery()
	query.max_results = 1000
	feed = client.GetContacts(q = query)

	print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>%s<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<' % len(feed.entry)
	print feed
	print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>><<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<'
	i = 0

	text = '<table border="1"><tr><td>Sl No</td><td>First Name</td><td>Last Name</td><td>Email</td><td>Contact Number</td></tr>'

	for a in feed.entry:
		text += '\n<tr>'
		i += 1
		text += '\n\t<td>%s</td>' % i

		print '>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>%s<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<' % i

		text += '\n\t<td>'
		try:
			print 'FN: ', a.name.given_name.text
			text += a.name.given_name.text
		except Exception, e:
			pass
		text += ' </td>'

		text += '\n\t<td>'
		try:
			print 'LN: ', a.name.family_name.text
			text += a.name.family_name.text
		except Exception, e:
			pass
		text += ' </td>'

		text += '\n\t<td>'
		try:
			for email in a.email:
				print '  %s' % (email.address)
				text += '%s</br>' % email.address
		except Exception, e:
			pass
		text += ' </td>'

		text += '\n\t<td>'
		try:
			for num in a.phone_number:
				print '  %s' % (num.uri)
				text += '%s</br>' % num.uri
		except Exception, e:
			pass
		text += ' </td>'

		text += '\n</tr>'
	text += '</table>'

	return '<a href="login">Here</a> <br> %s' % text

if __name__ == '__main__':
	app.debug = True
	app.run(host='0.0.0.0', port=8080)
