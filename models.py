from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from main import app, PASSWORD_REGEX, USERNAME_REGEX

# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(40))

    def __init__(self, username, password):
        if USERNAME_REGEX.match(username) == None:
            raise NameError
        if PASSWORD_REGEX.match(password) == None:
            raise ValueError
        self.username = username
        self.password = password

# Article Model
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    text = db.Column(db.String(1200))

    def __init__(self, title, text):
        self.title = title
        self.text = text

# User_schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username')

# Article Schema
class ArticleSchema(ma.Schema):
  class Meta:
    fields = ('id', 'title', 'text')

# Schema's initializing
article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)
user_schema = UserSchema()
