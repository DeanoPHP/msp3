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
from flask_pymongo import ObjectId
from functools import wraps


main = Blueprint("main", __name__)


def logged_in_user():
    """
    A decorator to restrict access to routes requiring authentication.

    - If the user is not logged in (i.e., "user" is not in session),
      flashes an error message and redirects them to the login page.
    - If the user is logged in, the wrapped function is executed as normal.

    Returns:
        function: The decorated function with authentication check.

    Usage:
        @logged_in_user()
        def protected_route():
            return "This route requires login"
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "user" not in session:
                flash("You need to be logged in to access this page.", "danger")
                return redirect(url_for("main.login"))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def get_current_user():
    """
    Gets the current logged in user

    return:
        dictionary: current users info
    """
    if "user" not in session:
        return None
    return mongo.db.users.find_one({
        "username": session["user"]
    })


# function to get the profile user or current user
def get_profile_user(username):
    """
    Gets the profile page user

    Args:
        username (str): username of the views profile page

    return:
        dictionary: profile owners information
    """
    return mongo.db.users.find_one({
        "username": username
    })


def get_business_owner(user_id):
    """
    Retrieves a business document owned by the specified user.

    - Queries the MongoDB 'business' collection for a document with an 'owner_id' that matches the provided user_id.
    
    Args:
        user_id (str): The unique identifier of the user who owns the business.

    Returns:
        dict or None: The business document if found, otherwise None.
    """
    return mongo.db.business.find_one({
        "owner_id": ObjectId(user_id)
    })


def get_business_reviews(owners_id):
    """
    Retrieves all reviews for a business using the owner's identifier.

    - Converts the provided owner_id to an ObjectId.
    - Queries the MongoDB 'reviews' collection for documents where the 'business_id' matches the converted owner_id.

    Args:
        owners_id (str): The unique identifier of the business owner, used as the business_id in reviews.

    Returns:
        list: A list of review documents associated with the business. If no reviews are found, returns an empty list.
    """
    return list(mongo.db.reviews.find({
        "business_id": ObjectId(owners_id)
    }))


@main.route("/")
def home():
    """Renders the home page"""
    return render_template("index.html")


@main.route("/about")
def about():
    """Renders the about page"""
    return render_template("about.html")


def getImages():
    """
    Handles image upload, encodes it in Base64, and returns the encoded data.

    This function checks if a file is uploaded under the "profile_image" key in the request.
    If a valid image file is found, it reads the file and encodes it in Base64 format.

    Returns:
        str or None: The Base64-encoded image data if successful, otherwise None.

    Raises:
        Exception: If an error occurs while reading the image, it logs the error,
                   flashes a failure message, and redirects to the registration page.
    """
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
    """
    Handles user registration.

    If the request method is POST, the function:
    - Checks if the username already exists in the database.
    - If the username exists, flashes an error message and redirects back to the form.
    - If not, processes the profile image (if provided).
    - Hashes the password and stores user details in the database.
    - Creates a session for the newly registered user.
    - Redirects to the login page with a success message.

    Returns:
        - If the method is GET: Renders the registration form.
        - If registration is successful: Redirects to the login page.
        - If the username already exists: Redirects to the registration form with an error message.
    """
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
    """
    Handles user login.

    If the request method is POST, the function:
    - Retrieves the user from the database using the provided email.
    - If the user exists, it verifies the password.
    - If the password is correct, creates a session and redirects the user to their profile page.

    Returns:
        - If the method is GET: Renders the login form.
        - If login is successful: Redirects to the user's profile page.
    """
    if request.method == "POST":
        check_user = mongo.db.users.find_one({
            "email": request.form.get("email").lower()
        })

        if check_user:
            if check_password_hash(check_user["password"], request.form.get("password")):
                # Create a session
                session["user"] = check_user["username"]
                flash("Welcome, {}".format(session["user"]), "success")
                return redirect(url_for("main.profile", username=session["user"]))
            else:
                flash("Incorrect password. Please try again.", "danger")
                return redirect(url_for("main.login"))

        flash("No user found","danger")
        return redirect(request.url)

    return render_template("login.html")


@main.route("/logout")
@logged_in_user()
def logout():
    """
    Handles user logout.

    - Removes the "user" session variable.
    - Flashes a success message to confirm logout.
    - Redirects the user to the homepage.

    Returns:
        Redirects to the homepage after logging out.
    """
    flash("You have been logged out", "success")
    session.pop("user")
    return redirect(url_for("main.home"))


@main.route("/profile/<username>")
@logged_in_user()
def profile(username):
    """
    Displays the profile page for a given username.

    - Retrieves the user's profile data from the database.
    - If the user is not found, flashes an error message and redirects to the homepage.
    - If the user exists, renders the profile page with the user's data.

    Args:
        username (str): The username of the profile to display.

    Returns:
        - Renders the "profile.html" template with the user's data if found.
        - Redirects to the homepage with an error message if no user is found.
    """
    profile_user = get_profile_user(username)

    if not profile_user:
        flash("No user found", "danger")
        return redirect(url_for("main.home"))
    
    get_business = get_business_owner(profile_user['_id'])
    
    if get_business:
        get_reviews = get_business_reviews(get_business["owner_id"])

        return render_template(
            "profile.html",
            username=username,
            business=get_business,
            user=profile_user,
            reviews=get_reviews
        )

    return render_template(
        "profile.html",
        username=username,
        user=profile_user
    )


@main.route("/edit_details/<user_id>", methods=["GET", "POST"])
@logged_in_user()
def edit_details(user_id):
    """
    Handles user profile updates.

    - Retrieves the current user's details from the database.
    - If the user does not exist, flashes an error message and redirects to the profile page.
    - Processes an optional profile image update.
    - Updates only the fields provided in the form, keeping existing values for empty fields.
    - Performs an update operation in the database.
    - If the update is successful, flashes a success message and redirects to the profile page.
    - If the update fails, flashes an error message.

    Args:
        user_id (str): The unique identifier of the user to update.

    Returns:
        - If the user is not found: Redirects to the profile page with an error message.
        - If the update is successful: Redirects to the profile page with a success message.
        - If an error occurs: Redirects to the profile page with an error message.
    """
    if request.method == "POST":
        # Fetch the current user details from the database
        current_user = get_current_user()

        if not current_user:
            flash("User not found", "danger")
            return redirect(url_for('main.profile', username=session['user']))

        image_data = getImages()

        # Build the updated details dictionary
        updated_details = {
            # Use old value if form is empty
            "email": request.form.get("email") or current_user["email"],
            "profile": {
                "name": request.form.get("name") or current_user["profile"]["name"],
                "postcode": request.form.get("postcode") or current_user["profile"]["postcode"],
                "bio": request.form.get("bio") or current_user["profile"]["bio"],
                "phoneNo": request.form.get("phoneNo") or current_user["profile"]["phoneNo"],
                "profile_image": image_data if image_data else current_user['profile']['profile_image']
            }
        }

        try:
            # Perform the update operation
            result = mongo.db.users.update_one(
                {"_id": ObjectId(user_id)},  # Match by ObjectId
                {"$set": updated_details}   # Set updated values
            )

            # Check if the update was successful
            if result.matched_count == 0:
                flash("User not found", "danger")
                return redirect(url_for('main.profile', username=session['user']))

            flash("Updated Successfully", "success")
            return redirect(url_for('main.profile', username=session['user']))
        except Exception as e:
            flash(f"An error occurred: {str(e)}", "danger")
            return redirect(url_for("main.profile", username=session['user']))


@main.route("/add_business/<user_id>", methods=["GET", "POST"])
@logged_in_user()
def add_business(user_id):
    """
    Handles the addition of a new business by a logged-in user.

    - Verifies that the user is logged in.
    - Checks if images are uploaded; if not, flashes a warning message.
    - Processes uploaded images by encoding them in Base64.
    - Collects business details from the form and constructs a business object.
    - Inserts the new business into the database.
    - Redirects the user back to their profile with a success or error message.

    Args:
        user_id (str): The unique identifier of the user adding the business.

    Returns:
        - If the user is not logged in: Redirects to the profile page with an error message.
        - If no images are uploaded: Redirects back to the form with a warning message.
        - If the business is successfully added: Redirects to the user's profile with a success message.
        - If an error occurs during insertion: Redirects to the profile page with an error message.
    """
    if request.method == "POST":

        current_user = get_current_user()

        if not current_user:
            flash("You must be a logged in user to create a business", "danger")
            return redirect(url_for("main.profile", username=current_user))

        if "business_images" not in request.files or not request.files.getlist("business_images"):
            flash("You have not uploaded any images", "warning")
            return redirect(request.url)

        # Get the files
        files = request.files.getlist('business_images')
        encoded_images = []

        # Process each image
        for file in files:
            if file:  # Ensure the file is not empty
                # Read image content
                image_content = file.read()
                # Encode image to Base64
                encoded_image = base64.b64encode(
                    image_content).decode("utf-8")
                encoded_images.append(encoded_image)

        business_to_add = {
            "owner_id": ObjectId(user_id),
            "company_name": request.form.get("company_name"),
            "description": request.form.get("description"),
            "location": request.form.get("location"),
            "category": request.form.get("category"),
            "images": encoded_images,
            "contact_info": {
                "email": request.form.get("email"),
                "phone": request.form.get("phone"),
                "website": request.form.get("website")
            }
        }

        create_business = mongo.db.business.insert_one(business_to_add)

        if not create_business:
            flash("Something has gone wrong", "danger")
            return redirect(url_for("main.profile", username=current_user['username']))

        flash("Your business has been added successfully", "success")
        print(current_user)
        return redirect(url_for("main.profile", username=current_user['username']))


@main.route("/add_review/<username>/<business_id>", methods=["GET", "POST"])
@logged_in_user()
def add_review(username, business_id):
    """
    Adds a review to a business associated with a user.

    - If 'business_id' equals "none", flashes an error and redirects to the user's profile.
    - On a POST request:
        * Retrieves the current logged-in user's details.
        * Retrieves the profile details for the given username.
        * Validates that a user is logged in; if not, flashes an error and redirects to the home page.
        * Constructs a review document containing:
            - business_id: Converted to an ObjectId.
            - user_id: Converted to an ObjectId from the current user's ID.
            - profile_image: Extracted from the current user's profile.
            - text: The review text from the form input named "reviews".
            - date: The review date from the form input named "datefeild".
        * Inserts the review into the MongoDB 'reviews' collection.
        * If the insertion fails, flashes an error and redirects to the profile page.
        * If the insertion is successful, flashes a success message and redirects to the profile page.

    Args:
        username (str): The username of the profile to which the review is being added.
        business_id (str): The identifier of the business. If "none", it indicates the absence of a business.

    Returns:
        Response: A Flask redirect response to either the user's profile page or the home page,
        depending on the outcome of the operation.
    """
    if business_id == "none":
        flash("This user does not have a business", "danger")
        return redirect(url_for("main.profile", username=session["user"]))

    if request.method == "POST":
        # Get all current user details
        current_user = get_current_user()
        profile = get_profile_user(username)

        if not current_user:
            flash("You need to be logged in to leave a review", "danger")
            return redirect(url_for("main.home"))

        create_review = {
            "business_id": ObjectId(business_id),
            "user_id": ObjectId(current_user["_id"]),
            "profile_image": current_user['profile']['profile_image'],
            "text": request.form.get("reviews"),
            "date": request.form.get("datefeild")
        }

        insert_review = mongo.db.reviews.insert_one(create_review)

        if not insert_review:
            flash("Sorry something went wrong", "danger")
            return redirect(url_for("main.profile", username=profile["username"]))

        flash("Review added successfully", "success")
        return redirect(url_for("main.profile", username=profile["username"]))


@main.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    """
    Edits an existing review.

    - On a POST request:
        * Retrieves the review corresponding to the provided review_id from the database.
        * If the review is not found, flashes an error message and redirects to the user's profile.
        * Constructs an updated review dictionary using the form inputs for the review text and date.
        * Updates the review document in the MongoDB 'reviews' collection.
        * If the update operation fails, flashes an error message and redirects to the referring page.
        * If the update is successful, flashes a success message and redirects to the referring page.
    - For non-POST requests, simply redirects to the referring page.

    Args:
        review_id (str): The unique identifier of the review to edit.

    Returns:
        Response: A Flask redirect response that either directs the user to the referring page or the profile page with an appropriate flash message.
    """
    if request.method == "POST":
        get_review = mongo.db.reviews.find_one({
            "_id": ObjectId(review_id)
        })

        if not get_review:
            flash("Sorry we are unable to find that review", "danger")
            return redirect(url_for("main.profile", username=session["user"]))

        updated_review = {
            "business_id": ObjectId(get_review["business_id"]),
            "user_id": ObjectId(get_review["user_id"]),
            "profile_image": get_review["profile_image"],
            "text": request.form.get("review"),
            "date": request.form.get("datefeild"),
        }

        update_to_db = mongo.db.reviews.update_one(
            {"_id": ObjectId(review_id)},
            {"$set": updated_review}
        )

        if not update_to_db:
            flash("Sorry something has gone wrong", "danger")
            return redirect(request.referrer)

        flash("Updated Successfully!!", "success")
        return redirect(request.referrer)

    return redirect(request.referrer)
