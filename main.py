import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore  
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.api import search

from models import User
from models import Post

from newuser import newuser
from blobstore import UploadHandler
from blobstore import ViewPhotoHandler
from profile import Profile
from search import Search

JINJA_ENVIRONMENT = jinja2.Environment(
loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
extensions = ['jinja2.ext.autoescape'],
autoescape = True)



class Insta(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "text/html"

        #self.redirect('/view_photo/%s' % Post.query().fetch()[0].image)

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
            
            all_users = []
            all_users.append(nickname)
            for user in user_key.get().following:
                all_users.append(user)
            
            posts = Post.query(Post.owner.email.IN(all_users)).order(-Post.timestamp).fetch(50)

            logout_url = users.create_logout_url('/')

            template_values = {
                'user': True,
                'login':'',
                'logout': logout_url,
                'name':nickname,
                'current_user':user_key.get(),
                'posts':posts
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
                    

app = webapp2.WSGIApplication([('/',Insta),
('/newuser',newuser),
('/upload_photo', UploadHandler),
('/view_photo/([^/]+)?', ViewPhotoHandler),
('/profile',Profile),   
('/search',Search)],debug = True)
