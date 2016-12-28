from flask import Flask
from app.extensions import mongo
from app.ws import music_ws

app = Flask(__name__)

# Configurations
app.config.from_object('config.Config')

# Define the database object which is imported by modules and controllers
mongo.init_app(app)

# Register blueprint(s)
app.register_blueprint(music_ws)

