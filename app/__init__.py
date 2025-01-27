import os
from flask import Flask
from dotenv import load_dotenv
from .routes import main
from .extensions import mongo, bcrypt


def create_app():
    app = Flask(__name__)

    load_dotenv()

    app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    mongo.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(main)

    return app