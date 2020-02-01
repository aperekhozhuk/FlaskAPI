from app import db
import os

try:
    os.remove('db.sqlite')
except:
    pass
db.create_all()
