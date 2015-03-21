"""`main` is the top level module for the Bottle application."""

import json

from google.appengine.api import urlfetch
from google.appengine.api import memcache
import bottle
from bottle import TEMPLATE_PATH,  jinja2_template as render

TEMPLATE_PATH.append("./templates")

bottle.debug(True)

# Create the Bottle WSGI application.
# Note: We don't need to call run() since our application is embedded within
# the App Engine WSGI application server.
#bottle = Bottle()

SITE_TITLE ="FG Dev Portal"

NAV = [
    {"page": "index", "title": "Welcome"},
    {"page": "codeissues", "title": "Code Issues"},
    {"page": "aircraftissues", "title": "Aircraft Issues"}
]

# Sourceforge API
# = https://sourceforge.net/p/forge/documentation/Allura%20API/#tracker"""

SF_URL = "http://sourceforge.net/rest/p/flightgear"
T_CODE = "codetickets"
T_ADDON = "tickets"


def make_payload():
    """Creates a default json payload (`success` is an Extjs thing)"""
    return dict(success=True, error=None)


def make_context():
    dic = {
        "site": {"title": SITE_TITLE, "nav": NAV},

    }
    return dic

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
		rows = decoded_data['tickets']
		memcache.set(ki, rows, time=60)
	return rows, None	
	

@bottle.route('/')
def index():
    c = make_context()
    return render("index.html", c=c)



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
