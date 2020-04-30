import webapp2
import jinja2
import os
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.api import search

from models import User
from models import Post


JINJA_ENVIRONMENT = jinja2.Environment(
loader = jinja2.FileSystemLoader(os.path.dirname(__file__)),
extensions = ['jinja2.ext.autoescape'],
autoescape = True)

def tokenize_autocomplete(phrase):
    a = []
    for word in phrase.split():
        j = 1
        while True:
            for i in range(len(word) - j + 1):
                a.append(word[i:i + j])
            if j == len(word):
                break
            j += 1
    return a

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
                new_key = user.put()
                
                email = new_key.get().email.split('@')[0]
                index = search.Index(name="user_search")
                doc_id = new_key.urlsafe()
                username = ','.join(tokenize_autocomplete(username))
                email = ','.join(tokenize_autocomplete(str(email)))
                document = search.Document(
                doc_id=doc_id,
                fields=[search.TextField(name='username', value=username),
                        search.TextField(name='email', value=email)])
                index.put(document)            

                self.redirect('/')
