import webapp2
import jinja2
import os
import datetime
from google.appengine.api import users
from google.appengine.ext import ndb
from google.appengine.ext.webapp import blobstore_handlers
from google.appengine.ext import blobstore



from models import User
from models import Post

class UploadHandler(blobstore_handlers.BlobstoreUploadHandler):
    def post(self):
        if self.request.get('button') == 'add_post':
            upload = self.get_uploads()[0]
            user =users.get_current_user()
            email = user.nickname()
            user_key = ndb.Key(User,email)
            current_user = user_key.get()
            caption = self.request.get('caption')

            user_photo = Post(image=upload.key(),
                            owner = current_user,
                            caption = caption,
                            timestamp= datetime.datetime.now())
            new_key = user_photo.put()

            self.redirect('/profile?key='+current_user.key.urlsafe())
        if self.request.get('button') == 'add_profile_pic':
            upload = self.get_uploads()[0]
            user =users.get_current_user()
            email = user.nickname()
            user_key = ndb.Key(User,email)
            current_user = user_key.get()
            current_user.profileImage = upload.key()

            key = current_user.put()

            self.redirect('/profile?key='+key.urlsafe())

class ViewPhotoHandler(blobstore_handlers.BlobstoreDownloadHandler):
    def get(self, photo_key):
        if not blobstore.get(photo_key):
            self.error(404)
        else:
            self.send_blob(photo_key)