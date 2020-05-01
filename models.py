from google.appengine.ext import ndb

class User(ndb.Model):
    email = ndb.StringProperty()
    username = ndb.StringProperty()
    followers = ndb.JsonProperty(repeated = True)
    following = ndb.JsonProperty(repeated = True)
    Posts = ndb.JsonProperty(repeated = True)
    profileImage = ndb.BlobKeyProperty()

class Comment(ndb.Model):
    author = ndb.StringProperty()
    author_email = ndb.StringProperty()
    comment = ndb.StringProperty()

class Post(ndb.Model):
    image =  ndb.BlobKeyProperty()
    owner = ndb.StructuredProperty(User)
    caption = ndb.StringProperty()
    timestamp = ndb.DateTimeProperty()
    comments = ndb.StructuredProperty(Comment, repeated = True)