from .api import app
from .api import db
db.create_all()
application = app
