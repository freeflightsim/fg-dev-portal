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
    {"page": "issues/code", "title": "Code Issues"},
    {"page": "issues/aircraft", "title": "Aircraft Issues"}
]

# Sourceforge API
# = https://sourceforge.net/p/forge/documentation/Allura%20API/#tracker"""

SF_API_URL = "http://sourceforge.net/rest/p/flightgear"
T_CODE = "codetickets"
T_ADDON = "tickets"


def make_payload():
    """Creates a default json payload (`success` is an Extjs thing)"""
    return dict(success=True, error=None)

class Context(object):

    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def make_context():
    """Creates a default pre-populated context for templates, c=c"""
    dic = {
        "site": {"title": SITE_TITLE, "nav": NAV},

    }
    return dic


def get_tickets(ticket_type):
	"""Tickets Summary"""
	ki = "summary_%s" % ticket_type
	rows = memcache.get(ki)
	
	if rows == None:
		url = SF_API_URL + "/%s?limit=3000" % ticket_type
		result = urlfetch.fetch(url)
		if result.status_code != 200:
			print "\tOOPS:" , result.status_code
			return None, result.status_code
		decoded_data = json.loads(result.content)
		rows = decoded_data['tickets']
		memcache.set(ki, rows, time=60)
	return rows, None	


#=========================================
# HTML Pages
#=========================================
@bottle.route('/')
@bottle.route('/index')
def index():
    c = make_context()
    return render("index.html", c=c)

@bottle.route('/issues/<issues_type>')
def issues(issues_type):
    c = make_context()
    c['issues_type'] = issues_type
    if not issues_type in ["code", "aircraft"]:
        c.error = 'Invalid issue type'
    else:
        sf_endpoint = T_CODE if issues_type == "code" else T_ADDON
        c.issues = get_tickets(sf_endpoint)
    return render("issues.html", c=c)

#=========================================
# Ajax
#=========================================
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
