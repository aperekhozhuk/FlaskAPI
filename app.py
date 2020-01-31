from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
import os
import jwt


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

# authorization decorator
def login_required(func):
    def wrapper(*args, **kwargs):
        token = request.json.get('token', None)
        if not token:
            return jsonify({'errors': 'Token is missing'})
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        except:
            return jsonify({'errors': 'Invalid token'})
        return func(*args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

# Create a new User
@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({'errors': 'username is missing'})
    if not password:
        return jsonify({'errors': 'password is missing'})
    new_user = User(username, password)
    try:
        db.session.add(new_user)
        db.session.commit()
        return user_schema.jsonify(new_user)
    except Exception:
        db.session().rollback()
        return jsonify({'errors': 'User with such username already exists'})

# User login
@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return jsonify({'errors': 'username is missing'})
    if not password:
        return jsonify({'errors': 'password is missing'})
    user = User.query.filter_by(username=username, password=password).first()
    if user:
        token = jwt.encode({'username': username, 'password': password}, app.config['SECRET_KEY'])
        return jsonify({'errors': '', 'user_id': user.id, 'username': user.username, 'token': token.decode('UTF-8')})
    return  jsonify({'errors': 'Uncorrect username or password'})

# Create a new Article
@app.route('/articles/new', methods=['POST'])
@login_required
def add_article():
    title = request.json.get('title', None)
    text = request.json.get('text', None)
    if not title:
        return jsonify({'errors': 'title is missing'})
    if not text:
        return jsonify({'errors': 'text is missing'})
    new_article = Article(title, text)
    db.session.add(new_article)
    db.session.commit()
    return article_schema.jsonify(new_article)

# Get All Articles
@app.route('/articles', methods=['GET'])
def get_articles():
    # Not good idea to load all articles. In future need to make pagination
    all_articles = Article.query.all()
    result = articles_schema.dump(all_articles)
    return jsonify(result)

# Get Single Article
@app.route('/articles/<id>', methods=['GET'])
def get_article(id):
    article = Article.query.get(id)
    if article:
        return article_schema.jsonify(article)
    return jsonify({'errors': 'Article with id={} not found'.format(id)})

# Update a Article
@app.route('/articles/edit/<id>', methods=['PUT'])
@login_required
def update_article(id):
    article = Article.query.get(id)
    if not article:
        return jsonify({'errors': 'Article with id={} not found'.format(id)})
    title = request.json.get('title', None)
    text = request.json.get('text', None)
    if not title:
        return jsonify({'errors': 'title is missing'})
    if not text:
        return jsonify({'errors': 'text is missing'})
    article.title = title
    article.text = text
    db.session.commit()
    return article_schema.jsonify(article)

# Delete Article
@app.route('/articles/delete/<id>', methods=['DELETE'])
@login_required
def delete_article(id):
    article = Article.query.get(id)
    if not article:
        return jsonify({'errors': 'Article with id={} not found'.format(id)})
    db.session.delete(article)
    db.session.commit()
    return article_schema.jsonify(article)

# Running app
if __name__ == '__main__':
    app.run(debug=True)