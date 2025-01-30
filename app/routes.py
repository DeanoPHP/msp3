from flask import (
    render_template, 
    Blueprint,
    request,
    flash,
    redirect,
    url_for,
    session
    )

from .extensions import mongo, bcrypt
import base64
from werkzeug.security import generate_password_hash, check_password_hash


main = Blueprint("main", __name__)


@main.route("/")
def home():
    return render_template("index.html")


@main.route("/about")
def about():
    return render_template("about.html")


def getImages():
    # Handle image upload
    image_data = None
    if "profile_image" in request.files:
        image_file = request.files["profile_image"]
        if image_file.filename != "":
            try:
                # Read the image file and encode it as Base64
                image_data = base64.b64encode(
                    image_file.read()).decode("utf-8")
                return image_data
            except Exception as e:
                print("Error reading image:", e)
                flash("Failed to process profile image.", "danger")
                return redirect(url_for("main.register"))


@main.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # Check the user doesn't already exist
        existing_user = mongo.db.users.find_one({
            "username": request.form.get("username")
        })

        if existing_user:
            flash("A userwith that username already exist", "danger")
            return redirect(request.url)
        
        image_data = getImages()
        
        # register the user
        register = {
            "username": request.form.get("username"),
            "email": request.form.get("email"),
            "password": generate_password_hash(request.form.get("password")),
            "profile": {
                "name": request.form.get("name"),
                "postcode": request.form.get("postcode"),
                "bio": request.form.get("bio"),
                "phoneNo": request.form.get("phoneNo"),
                "profile_image": image_data
            }
        }

        mongo.db.users.insert_one(register)

        # Create a session for the user 
        session["user"] = request.form.get("username").lower()
        flash("Congratulations and welcome to mind your own business.", "success")
        return redirect(url_for("main.login"))

    return render_template("register.html")


@main.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        check_user = mongo.db.users.find_one({
            "email": request.form.get("email").lower()
        })

        if check_user:
            check_password_hash(
                check_user["password"], request.form.get("password")
            )

            # Create a session
            session["user"] = check_user["username"]
            flash("Welcome, {}".format(
                session["user"]
            ))
            return redirect(url_for("main.profile"))

    return render_template("login.html")


@main.route("/logout")
def logout():
    flash("You have been logged out", "success")
    session.pop("user")
    return redirect(url_for("main.home"))


@main.route("/profile")
def profile():
    return render_template("profile.html")