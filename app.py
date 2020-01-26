from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
import os

# Init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
# Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Init db
db = SQLAlchemy(app)
# Init ma
ma = Marshmallow(app)

# Article Model
class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), unique=True)
    text = db.Column(db.String(1200))

    def __init__(self, title, text):
        self.title = title
        self.text = text

# Article Schema
class ArticleSchema(ma.Schema):
  class Meta:
    fields = ('id', 'title', 'text')

# Init schema
article_schema = ArticleSchema()
articles_schema = ArticleSchema(many=True)


if __name__ == '__main__':
    app.run(debug=True)