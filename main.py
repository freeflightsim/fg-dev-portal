"""`main` is the top level module for the Bottle application."""

import json

from google.appengine.api import urlfetch
from google.appengine.api import memcache
import bottle

bottle.debug(True)

# Create the Bottle WSGI application.
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
#bottle = Bottle()


# Sourceforge API
# = https://sourceforge.net/p/forge/documentation/Allura%20API/#tracker"""

SF_URL = "http://sourceforge.net/rest/p/flightgear"
T_CODE = "codetickets"
T_ADDON = "tickets"

"""Creates a default payload (`success` is an Extjs thing)"""
def make_payload():
	return dict(success=True, error=None)


"""Tickets Summary"""	
def get_tickets(what):
	
	ki = "summary_%s" % what
	rows = memcache.get(ki)
	
	if rows == None:
		url = SF_URL + "/%s?limit=3000" % T_CODE
		result = urlfetch.fetch(url)
		if result.status_code != 200:
			print "\tOOPS:" , result.status_code
			return None, result.status_code
		decoded_data = json.loads(result.content)
		print "DEC:" , decoded_data.keys()
		rows = decoded_data['tickets']
		memcache.set(ki, rows, time=60)
	return rows, None	
	

@bottle.route('/')
def index():
   
    return 'Hello FsssssssssG'



@bottle.route('/ajax/tickets/code')
def ajax_tickets_code():

	payload = make_payload()
	
	payload['tickets'], payload['error'] = get_tickets(T_CODE)
	
	
	return payload



# Define an handler for 404 errors.
@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'


app = bottle.default_app()
