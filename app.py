import os
from app import create_app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.environ.get("IP"),
        port=os.environ.get("PORT"),
        debug=os.environ.get("DEBUG")
    )