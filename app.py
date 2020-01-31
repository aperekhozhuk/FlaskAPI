from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os

####### App Settings

# Init app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'A16RoTodXyMxiGgbvkuk'
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

#### Models and Schemas

# User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(40))

    def __init__(self, username, password):
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

# Init schema
article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)
user_schema = UserSchema()

#################   ROUTES

# Create a new User
@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    password = request.json['password']
    new_user = User(username, password)
    db.session.add(new_user)
    db.session.commit()
    return user_schema.jsonify(new_user)

# User login
@app.route('/login', methods=['POST'])
def login():
    username = request.json['username']
    password = request.json['password']
    user = User.query.filter_by(username=username, password=password).first()
    return  user_schema.jsonify(user)

# Create a new Article
@app.route('/articles/new', methods=['POST'])
def add_article():
    title= request.json['title']
    text = request.json['text']
    new_article = Article(title, text)
    db.session.add(new_article)
    db.session.commit()
    return article_schema.jsonify(new_article)

# Get All Articles
@app.route('/articles', methods=['GET'])
def get_articles():
    all_articles = Article.query.all()
    result = articles_schema.dump(all_articles)
    return jsonify(result)

# Get Single Article
@app.route('/articles/<id>', methods=['GET'])
def get_article(id):
    article = Article.query.get(id)
    return article_schema.jsonify(article)

# Update a Article
@app.route('/articles/edit/<id>', methods=['PUT'])
def update_article(id):
    article = Article.query.get(id)
    title = request.json['title']
    text = request.json['text']
    article.title = title
    article.text = text
    db.session.commit()
    return article_schema.jsonify(article)

# Delete Article
@app.route('/articles/delete/<id>', methods=['DELETE'])
def delete_article(id):
    article = Article.query.get(id)
    db.session.delete(article)
    db.session.commit()
    return article_schema.jsonify(article)

# Running app
if __name__ == '__main__':
    app.run(debug=True)