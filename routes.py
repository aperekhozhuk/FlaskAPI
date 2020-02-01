from flask import request, jsonify
import jwt
from models import db, User, Article, user_schema, articles_schema, article_schema
from main import app


# authorization decorator
def login_required(func):
    def wrapper(*args, **kwargs):
        token = request.json.get('token', None)
        if not token:
            return jsonify({'errors': 'Token is missing'})
        try:
            payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
            # If decoding was success - it's no guarantee,
            # that such user really registered
            # Need to check
            user = User.query.filter_by(
                username = payload['username'],
                password = payload['password']
            ).first()
            # If user was not found - raise Exception.
            # It breaks us to next exception handler
            if not user:
                raise Exception
        except:
            return jsonify({'errors': 'Invalid token'})
        # Now, we can call our route function and pass valid user to it
        return func(user, *args, **kwargs)
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
    try:
        new_user = User(username, password)
    except NameError:
        return jsonify({'errors': 'username regex error'}), 400
    except ValueError:
        return jsonify({'errors': 'password regex error'}), 400
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
def add_article(user):
    title = request.json.get('title', None)
    text = request.json.get('text', None)
    if not title:
        return jsonify({'errors': 'title is missing'})
    if not text:
        return jsonify({'errors': 'text is missing'})
    new_article = Article(user.id, title, text)
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
def update_article(user, id):
    article = Article.query.get(id)
    if not article:
        return jsonify({'errors': 'Article with id={} not found'.format(id)})
    if article.user_id != user.id:
        return jsonify({'errors': 'You can edit only own post'})
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
def delete_article(user, id):
    article = Article.query.get(id)
    if not article:
        return jsonify({'errors': 'Article with id={} not found'.format(id)})
    if article.user_id != user.id:
        return jsonify({'errors': 'You can delete only own post'})
    db.session.delete(article)
    db.session.commit()
    return article_schema.jsonify(article)

@app.route('/users/<id>', methods=['GET'])
def user_data(id):
    user = User.query.get(id)
    if not user:
        return jsonify({'errors': 'User with id={} not found'.format(id)})
    return user_schema.jsonify(user)