import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb

from models import User
from models import Post

from newuser import newuser


JINJA_ENVIRONMENT = jinja2.Environment(
loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
extensions = ['jinja2.ext.autoescape'],
autoescape = True)

class Insta(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "text/html"

        user =users.get_current_user()

        template_values = {
            'user':False,
            'login': '',
            'logout': '',
            'name':''
        }

        if user:
            nickname = user.nickname()

            user_key = ndb.Key(User,nickname)

            if user_key.get() == None:
                new_user = User(id=nickname)
                new_user.email = nickname
                new_key = new_user.put()
                self.redirect('/newuser?key='+new_key.urlsafe())
            else:
                current_user = user_key.get()
                if current_user.username == None:
                    self.redirect('/newuser?key='+user_key.urlsafe())
            
            logout_url = users.create_logout_url('/')
            template_values = {
                'user': True,
                'login':'',
                'logout': logout_url,
                'name':nickname,
                'username':user_key.get().username 
            }
        else:
            login_url = users.create_login_url('/')
            template_values = {
                'user': False,
                'login': login_url,
                'logout': '',
                'name':''
            }
    
        template = JINJA_ENVIRONMENT.get_template('main.html')
        self.response.write(template.render(template_values))

app = webapp2.WSGIApplication([('/',Insta),('/newuser',newuser)],debug = True)
