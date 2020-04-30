import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext import blobstore  
from google.appengine.ext.webapp import blobstore_handlers

from models import User
from models import Post

from newuser import newuser
from blobstore import UploadHandler
from blobstore import ViewPhotoHandler


JINJA_ENVIRONMENT = jinja2.Environment(
loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
extensions = ['jinja2.ext.autoescape'],
autoescape = True)

class Profile(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = "text/html"

        user_key = self.request.get('key')
        user_key = ndb.Key(urlsafe=user_key)
        #self.response.write(user_key)

        user = users.get_current_user()

        template_values = {
            'user':False,
            'login': '',
            'logout': '',
            'name':''
        }

        if user:
            nickname = user.nickname()

            current_user_key = ndb.Key(User,nickname)

            if current_user_key.get() == None:
                new_user = User(id=nickname)
                new_user.email = nickname
                new_key = new_user.put()
                self.redirect('/newuser?key='+new_key.urlsafe())
            else:
                current_user = current_user_key.get()
                if current_user.username == None:
                    self.redirect('/newuser?key='+current_user_key.urlsafe())

            logout_url = users.create_logout_url('/')

            profile_posts = Post.query(Post.owner.email == user_key.get().email).fetch()


            template_values = {
                'user': True,
                'login':'',
                'logout': logout_url,
                'name':nickname,
                'current_profile':user_key.get(),
                'current_user': current_user_key.get(),
                'profile_posts':profile_posts
            }

            if current_user_key == user_key:
                template_values['owner'] = True
                template_values['post_image'] = blobstore.create_upload_url('/upload_photo')
            else:
                template_values['owner'] = False
            if user_key.get().email in current_user_key.get().following:
                template_values['following'] = True
            else:
                template_values['following'] = False
            
        else:
            login_url = users.create_login_url('/')
            profile_posts = Post.query(Post.owner.email == user_key.get().email).fetch()
            template_values = {
                'user': False,
                'login': login_url,
                'logout': '',
                'name':'',
                'current_profile':user_key.get(),
                'current_user': None,
                'profile_posts':profile_posts
            }

        template = JINJA_ENVIRONMENT.get_template('profile.html')
        self.response.write(template.render(template_values))
    
    def post(self):
        if self.request.get('button') == 'delete_post':
            post_key = ndb.Key(urlsafe = self.request.get('post_key'))
            post_key.delete()

            self.redirect('/profile?key='+self.request.get('user_key'))