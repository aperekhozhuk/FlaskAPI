import os
import re


basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SECRET_KEY = 'A16RoTodXyMxiGgbvkuk'   # It's joke.Of course I replaced it on production server before deployment))
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # Page size (need for paginations)
    POSTS_PER_PAGE = 10
    # Username and Password regexes for validation
    PASSWORD_REGEX = re.compile(
        "^(?=.*?[A-Z])(?=.*?[a-z])(?=.*?[0-9])(?=.*?[!@#$%^&*\\-_])" +\
            "[A-Za-z0-9!@#$%^&*\\-_]{8,40}$"
    )
    USERNAME_REGEX = re.compile(
        "^[A-Za-z0-9!@#$%^&*\\-_]{5,20}$"
    )
