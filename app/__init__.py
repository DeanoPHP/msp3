from flask import Flask
from dotenv import load_dotenv
from .routes import main


def create_app():
    app = Flask(__name__)

    load_dotenv()

    app.register_blueprint(main)

    return app