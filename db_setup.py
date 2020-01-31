from app import db
import os

os.remove('db.sqlite')
db.create_all()
