from google.appengine.ext import ndb

class User(ndb.Model):
    email = ndb.StringProperty()
    username = ndb.StringProperty()
    followers = ndb.JsonProperty(repeated = True)
    following = ndb.JsonProperty(repeated = True)
    Posts = ndb.JsonProperty(repeated = True)
    profileImage = ndb.BlobKeyProperty()

class Post(ndb.Model):
    image =  ndb.BlobKeyProperty()
    owner = ndb.StructuredProperty(User)
    caption = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty()
