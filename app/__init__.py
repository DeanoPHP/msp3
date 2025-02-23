import os
from flask import Flask
from dotenv import load_dotenv
from .routes import main
from .extensions import mongo, bcrypt


def create_app():
    app = Flask(__name__)

    load_dotenv()
    app.config["GOOGLE_MAPS_API_KEY"] = os.getenv("GOOGLE_MAPS_API_KEY")

    app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
    app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")

    mongo.init_app(app)
    bcrypt.init_app(app)

    app.register_blueprint(main)

    # Make API key available globally in templates
    @app.context_processor
    def inject_google_maps_key():
        return dict(GOOGLE_MAPS_API_KEY=app.config["GOOGLE_MAPS_API_KEY"])

    return app