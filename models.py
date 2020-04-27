from google.appengine.ext import ndb

class User(ndb.Model):
    email = ndb.StringProperty()
    username = ndb.StringProperty()
    followers = ndb.JsonProperty(repeated = True)
    following = ndb.JsonProperty(repeated = True)

class Post(ndb.Model):
    image =  ndb.BlobKeyProperty()
    username = ndb.StringProperty()
    email = ndb.StringProperty()
    caption = ndb.StringProperty()

