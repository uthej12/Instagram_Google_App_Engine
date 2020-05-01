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
from models import Comment

from newuser import newuser
from blobstore import UploadHandler
from blobstore import ViewPhotoHandler
from profile import Profile
from search import Search
from displayPost import displayPost

JINJA_ENVIRONMENT = jinja2.Environment(
loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
extensions = ['jinja2.ext.autoescape'],
autoescape = True)


def return_url_key(email):
    return ndb.Key(User,email).urlsafe()

def user_object(email):
    return ndb.Key(User,email).get()

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
                'posts':posts,
                'return_user_url': return_url_key,
                'user_object': user_object
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

    def post(self):
        self.response.write(self.request.get('button'))
        if self.request.get('button') == 'addComment':
            post_key = self.request.get('post_key')
            comment_text = self.request.get('comment_'+post_key)

            post = ndb.Key(urlsafe = post_key).get()
            current_user = ndb.Key(User, users.get_current_user().nickname()).get()  
            new_comment = Comment(author = current_user.username,
                                author_email = current_user.email,
                                comment = comment_text)
            post.comments.append(new_comment)
            post.put()

            self.redirect('/')
                    

app = webapp2.WSGIApplication([('/',Insta),
('/newuser',newuser),
('/upload_photo', UploadHandler),
('/view_photo/([^/]+)?', ViewPhotoHandler),
('/profile',Profile),   
('/search',Search),
('/post',displayPost)],debug = True)
