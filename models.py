from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from main import app, PASSWORD_REGEX, USERNAME_REGEX
from datetime import datetime

# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)


# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(40))

    articles = db.relationship('Article', backref='author', lazy='dynamic')

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
    title = db.Column(db.Text)
    text = db.Column(db.Text)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, user_id, title, text):
        self.user_id = user_id
        self.title = title
        self.text = text

# User_schema
class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username')

# Article Schema
class ArticleSchema(ma.Schema):
  class Meta:
    fields = ('id', 'title', 'text', 'user_id', 'date_posted')

# Articles Schema
class ArticlesSchema(ma.Schema):
  class Meta:
    fields = ('id', 'title', 'user_id', 'date_posted')

# Schema's initializing
article_schema = ArticleSchema()
articles_schema = ArticlesSchema(many=True)
user_schema = UserSchema()