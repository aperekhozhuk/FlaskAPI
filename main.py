from flask import Flask
from flask_cors import CORS
import os
import re

# Init app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'A16RoTodXyMxiGgbvkuk'
CORS(app)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Username and Password regexes for validation
PASSWORD_REGEX = re.compile(
    "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#$%^&*-_]).{8,40}$"
)
USERNAME_REGEX = re.compile(
    "^[A-Za-z\d!@#$%^&*-_]{5,20}$"
)
# Paginated collection size
POSTS_PER_PAGE = 10
