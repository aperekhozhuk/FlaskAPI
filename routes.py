from flask import request, jsonify
import jwt
from models import db, User, Article, user_schema, \
    articles_schema, article_schema
from main import app, POSTS_PER_PAGE


# Helper functions:

def user_exists(username, password):
    """
    Returns User with specified credentials if it exists,
    or None otherwise
    """
    user = User.query.filter_by(username = username).first()
    if user and user.password == password:
        return user
    return None

def login_required(func):
    """
    Authentication decorator, which run 'func' if request was
    sent from valid user. Otherwise returns JSON response with error explanation
    """
    def wrapper(*args, **kwargs):
        token = request.json.get('access-token', None)
        if not token:
            return jsonify({
                'error': 'Access-token is missing. Log in, please'
            }), 401
        try:
            # Handling token DecodeError
            payload = jwt.decode(
                token, app.config['SECRET_KEY'], algorithms=['HS256']
            )
            # If payload data is valid - left to check,
            # if such user really exists
            user = user_exists(payload['username'], payload['password'])
            if not user:
                raise Exception
        # If token is invalid
        except Exception:
            return jsonify({
                'error': 'Invalid access-token. Log in please'
            }), 401
        # Now, we can call our route function and pass valid user to it
        return func(user, *args, **kwargs)
    wrapper.__name__ = func.__name__
    return wrapper

def resource_not_found_message(resource_type, resource_id):
    error = '{} with id={} was not found'.format(resource_type, resource_id)
    return jsonify({'error': error})

def article_forbidden_action_message(action):
    return jsonify({'error': 'You can {} only own article'.format(action)})

def field_is_missing_message(field_type):
    return jsonify({'error': '{} is missing'.format(field_type)})


# Routes:

# User registration
@app.route('/register', methods=['POST'])
def register():
    """
    Register new user with credentials passed in request body,
    or return JSON response with error explanation
    """
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return field_is_missing_message(field_type = 'Username'), 400
    if not password:
        return field_is_missing_message(field_type = 'Password'), 400
    # Trying to create User object. Handle bad format exceptions(See models)
    try:
        new_user = User(username, password)
    except NameError:
        # If username doesn't satisfy regex
        return jsonify({'error': 'Bad username format'}), 400
    except ValueError:
        # If password doesn't satisfy regex
        return jsonify({'error': 'Bad password format'}), 400
    # Trying to add new user to database.
    # Need to handle cases if user name already used
    try:
        db.session.add(new_user)
        db.session.commit()
        return user_schema.jsonify(new_user), 200
    except Exception:
        db.session().rollback()
        return jsonify({
            'error': 'User with such name already exists'
        }), 409

# User log in
@app.route('/login', methods=['POST'])
def login():
    """
    Trying to log in with credentials from request body.
    In case of success returns access-token, or error explanation otherwise.
    """
    username = request.json.get('username', None)
    password = request.json.get('password', None)
    if not username:
        return field_is_missing_message(field_type = 'Username'), 400
    if not password:
        return field_is_missing_message(field_type = 'Password'), 400
    user = user_exists(username, password)
    if user:
        token = jwt.encode(
            {'username': username, 'password': password},
            app.config['SECRET_KEY']
        )
        return jsonify({
            'user_id': user.id,
            'username': user.username,
            'access-token': token.decode('UTF-8')
        }), 200
    return  jsonify({'error': 'Uncorrect username or/and password'}), 401

# Add new article
@app.route('/articles/new', methods=['POST'])
@login_required
def add_article(user):
    """
    Create new article for current user
    """
    title = request.json.get('title', None)
    text = request.json.get('text', None)
    if not title:
        return field_is_missing_message(field_type = 'Article title'), 400
    if not text:
        return field_is_missing_message(field_type = 'Article text'), 400
    new_article = Article(user.id, title, text)
    db.session.add(new_article)
    db.session.commit()
    return article_schema.jsonify(new_article), 200

# Get last articles
@app.route('/articles', methods=['GET'])
def get_articles():
    """
    Returns last articles as paginated collection.
    Page size specified in project global variable 'POSTS_PER_PAGE'
    """
    # Trying to parse page number from request parameters.
    # By default returns first page
    page = request.args.get('page', 1, type = int)

    last_articles = Article.query.order_by(Article.date_posted.desc()). \
        paginate(page = page, per_page = POSTS_PER_PAGE, error_out = False)

    result = articles_schema.dump(last_articles.items)
    return jsonify(result), 200

# Get single article
@app.route('/articles/<id>', methods=['GET'])
def get_article(id):
    """
    Return article with specified id.
    Or 404 if such article was not found
    """
    article = Article.query.get(id)
    if not article:
        return resource_not_found_message('Article', id), 404
    return article_schema.jsonify(article), 200

# Edit article
@app.route('/articles/<id>/edit', methods=['PUT'])
@login_required
def update_article(user, id):
    """
    Update article only if it belongs to current user
    """
    article = Article.query.get(id)
    if not article:
        return resource_not_found_message('Article', id), 404

    if article.user_id != user.id:
        return article_forbidden_action_message(action = 'edit'), 403

    title = request.json.get('title', None)
    text = request.json.get('text', None)
    if not title:
        return field_is_missing_message(field_type = 'Article title'), 400
    if not text:
        return field_is_missing_message(field_type = 'Article text'), 400
    article.title = title
    article.text = text
    db.session.commit()
    return article_schema.jsonify(article), 200

# Delete article
@app.route('/articles/<id>/delete', methods=['DELETE'])
@login_required
def delete_article(user, id):
    """
    Delete article only if it belongs to current user
    """
    article = Article.query.get(id)
    if not article:
        return resource_not_found_message('Article', id), 404
    if article.user_id != user.id:
        return article_forbidden_action_message(action = 'delete'), 403
    db.session.delete(article)
    db.session.commit()
    return article_schema.jsonify(article), 200

# Get user data
@app.route('/users/<id>', methods=['GET'])
def user_data(id):
    """
    Get public user data. In future it can be: avatar,
    rank, nickname, date of ragistration etc.
    """
    user = User.query.get(id)
    if not user:
        return resource_not_found_message('User', id), 404
    return user_schema.jsonify(user), 200

# Return last user's articles
@app.route('/users/<id>/articles', methods=['GET'])
def user_articles(id):
    """
    Return user's last articles as paginated collection.
    Page number retrives from as request parameter
    """
    page = request.args.get('page', 1, type=int)
    user = User.query.get(id)
    if not user:
        return resource_not_found_message('User', id), 404

    user_articles = user.articles.order_by(Article.date_posted.desc()) \
        .paginate(page = page, per_page = POSTS_PER_PAGE, error_out = False)

    result = articles_schema.dump(user_articles.items)
    return articles_schema.jsonify(result), 200
