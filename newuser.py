import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb

from models import User
from models import Post


JINJA_ENVIRONMENT = jinja2.Environment(
loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
extensions = ['jinja2.ext.autoescape'],
autoescape = True)

class newuser(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "text/html"

        user = users.get_current_user()

        urlsafe_key = self.request.get('key')

        template_values = {
            'key' :urlsafe_key
        }

        if len(self.request.get('error')) > 2:
            template_values['error'] = 'true'
        else:    
            template_values['error'] = 'false'
    
        template = JINJA_ENVIRONMENT.get_template('newuser.html')
        self.response.write(template.render(template_values))

    def post(self):
        if self.request.get('button') == 'addUser':
            user_key = self.request.get('key')
            username = self.request.get('username')
            query = User.query(User.username == username).fetch()
            if len(query) > 0:
                self.redirect('/newuser?key='+user_key+"&error=yes")
            else:
                user_key = ndb.Key(urlsafe = user_key)
                user = user_key.get()
                user.username = username
                user.put()
                self.redirect('/')
