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


JINJA_ENVIRONMENT = jinja2.Environment(
loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
extensions = ['jinja2.ext.autoescape'],
autoescape = True)



class Search(webapp2.RequestHandler):
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
            
            user_posts = Post.query(Post.owner.email == nickname).fetch()

            logout_url = users.create_logout_url('/')

            template_values = {
                'user': True,
                'login':'',
                'logout': logout_url,
                'name':nickname,
                'current_user':user_key.get(),
            }
        else:
            login_url = users.create_login_url('/')
            template_values = {
                'user': False,
                'login': login_url,
                'logout': '',
                'name':''
            }

        if self.request.get('button') == 'search':
            query = self.request.get('search_string')
            template_values['query'] = query

            if '@' in list(query):
                query = query.split('@')[0]

            breakpoints ="! % ( ) * , - | / [ ] ] ^ ` : = > ? { } ~ $"
            breakpoints = breakpoints.split(' ')

            temp = list(query)
            for point in breakpoints:
                if point in temp: 
                    temp.remove(point)
                    query = ''.join(temp)
                    temp = list(query)

                
            if len(query) == 0:
                s = User.query().fetch(50)
                results = []
                for user in s:
                    results.append(user.key)
                template_values['search_results'] = results
            else:
                if len(query.split('.')) > 1:
                    new_query = ''
                    for word in query.split('.'):
                        new_query = new_query+' '+str(word)
                    query = new_query
                results = search.Index(name='user_search').search('username:'+query)
                email_results = search.Index(name='user_search').search('email:'+query)
                
                search_results = []
                for item in results:
                    urlsafe_key = item.doc_id
                    key = ndb.Key(urlsafe = urlsafe_key)
                    if key not in search_results:
                        search_results.append(key)
                for item in email_results:
                    urlsafe_key = item.doc_id
                    key = ndb.Key(urlsafe = urlsafe_key)
                    if key not in search_results:
                        search_results.append(key)
                template_values['search_results'] = search_results

        

        template = JINJA_ENVIRONMENT.get_template('search.html')
        self.response.write(template.render(template_values))
