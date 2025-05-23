import os
import requests
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


def get_lat_lng(address):
    """
    Retrieves the latitude and longitude for a given address using the Google Geocoding API.

    This function takes a single address as input and makes a request to the Google Geocoding API.
    It parses the JSON response to extract the latitude and longitude of the address. If the address
    is empty or the API response is not successful, it returns (None, None).

    Args:
        address (str): The address for which to retrieve the geographical coordinates.

    Returns:
        tuple: A tuple containing the latitude and longitude of the given address. If the address
            is invalid or an error occurs in the API call, returns (None, None).
    """
    if not address:
        return None, None
    api_key = os.getenv("GOOGLE_MAPS_API_KEY")
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={api_key}"
    response = requests.get(url).json()
    if response["status"] == "OK":
        location = response["results"][0]["geometry"]["location"]
        return location["lat"], location["lng"]
    return None, None


@main.route("/")
def home():
    """Renders the home page"""
    return render_template("index.html")


@main.route("/about")
def about():
    """Renders the about page"""
    return render_template("about.html")


def getImages(image_name):
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
    if image_name in request.files:
        image_file = request.files[image_name]
        if image_file.filename != "":
            try:
                # Read the image file and encode it as Base64
                image_data = base64.b64encode(
                    image_file.read()).decode("utf-8")
                return image_data
            except Exception as e:
                print("Error reading image:", e)
                flash(f"Failed to process {image_name}.", "danger")
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
            "username": request.form.get("username").lower()
        })

        if existing_user:
            flash("A user with that username already exist", "danger")
            return redirect(request.url)

        image_data = getImages("profile_image")

        register = {
            "username": request.form.get("username").lower(),
            "email": request.form.get("email").lower(),
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
                session["user"] = check_user["username"]

                # Check whether the user has a session[next]
                if "next" in session:
                    url = session.pop("next")
                    flash("We noticed you tryed searching this page before logging in", "success")
                    return redirect(url)

                flash("Welcome, {}".format(session["user"]), "success")
                return redirect(url_for("main.profile", username=session["user"]))
            else:
                flash("Incorrect password. Please try again.", "danger")
                return redirect(url_for("main.login"))

        flash("No user found", "danger")
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

    get_business = get_business_owner(profile_user["_id"])

    get_all_businesses = mongo.db.business.find_one({
        "owner_id": ObjectId(profile_user['_id'])
    })

    # Default lat/lng to None
    lat, lng = None, None

    if get_business:
        # Ensure get_lat_lng() does not break if location is missing
        if "location" in get_all_businesses and get_all_businesses["location"]:
            lat, lng = get_lat_lng(get_all_businesses["location"])

        get_reviews = get_business_reviews(get_business["owner_id"])

        get_deal = mongo.db.deals.find_one({
            "business_owner": ObjectId(profile_user["_id"])
        })

        return render_template(
            "profile.html",
            username=username,
            business=get_business,
            user=profile_user,
            reviews=get_reviews,
            lat=lat,
            lng=lng,
            get_all_businesses=get_all_businesses,
            deal=get_deal or None
        )

    # If the user does not own a business, still return lat/lng as None
    return render_template(
        "profile.html",
        username=username,
        user=profile_user,
        business=None,
        reviews=None,
        lat=None,
        lng=None,
        get_all_businesses=None,
        deal=None
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

        image_data = getImages("profile_image")

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
    """
    if request.method == "POST":
        current_user = get_current_user()

        if not current_user:
            flash("You must be logged in to create a business", "danger")
            return redirect(url_for("main.profile", username=current_user))

        if "business_images" not in request.files or not request.files.getlist("business_images"):
            flash("You have not uploaded any images", "warning")
            return redirect(request.url)

        # Get category (Ensure it is not None)
        category = request.form.get("category")

        if not category:
            flash("Please select a category for your business.", "danger")
            return redirect(request.url)

        # Get the files
        files = request.files.getlist("business_images")
        encoded_images = []

        # Process each image
        for file in files:
            if file:  # Ensure the file is not empty
                image_content = file.read()
                encoded_image = base64.b64encode(image_content).decode("utf-8")
                encoded_images.append(encoded_image)

        business_to_add = {
            "owner_id": ObjectId(user_id),
            "company_name": request.form.get("company_name"),
            "description": request.form.get("description"),
            "location": request.form.get("location"),
            "category": category,  # ✅ Ensure category is added
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
        return redirect(url_for("main.profile", username=current_user['username']))


@main.route("/edit_business/<business_id>", methods=["GET", "POST"])
def edit_business(business_id):
    """
    Handles business profile updates.

    - Retrieves the current business details from the database.
    - If the business does not exist, flashes an error message and redirects to the profile page.
    - Retrieves form data for business updates (name, description, location, etc.).
    - Processes optional image uploads while retaining existing images if none are uploaded.
    - Updates only the fields provided in the form, keeping existing values for empty fields.
    - Performs an update operation in the database.
    - If the update is successful, flashes a success message and redirects to the profile page.

    Args:
        business_id (str): The unique identifier of the business to update.

    Returns:
        - If the business is not found: Redirects to the profile page with an error message.
        - If the update is successful: Redirects to the profile page with a success message.
    """

    # Retrieve the business from the database
    business = mongo.db.business.find_one({'_id': ObjectId(business_id)})

    # If business does not exist, flash an error and redirect
    if not business:
        flash("We cannot find that business", "danger")
        return redirect(url_for("main.profile", username=session["user"]))

    # Retrieve form data from the request
    company_name = request.form.get("company_name")
    description = request.form.get("description")
    location = request.form.get("location")
    category = request.form.get("category")
    email = request.form.get("email")
    phone = request.form.get("phone")
    website = request.form.get("website")

    # Retrieve uploaded images from the request
    new_images = request.files.getlist('business_images')

    # Keep existing images if no new ones are uploaded
    image_list = business['images'] if business and 'images' in business else [
    ]

    # Convert and append new images to the list if provided
    for image in new_images:
        if image and image.filename != '':
            image_list.append(base64.b64encode(image.read()).decode('utf-8'))

    # Prepare the updated business data
    updated_business = {
        "company_name": company_name,
        "description": description,
        "location": location,
        "category": category,
        "images": image_list,  # Retain old images if no new ones are uploaded
        "contact_info": {
            "email": email,
            "phone": phone,
            "website": website
        }
    }

    # Perform the update operation in the database
    mongo.db.business.update_one({'_id': ObjectId(business_id)}, {
                                 '$set': updated_business})

    # Flash a success message and redirect to the profile page
    flash("Business details updated successfully", "success")
    return redirect(url_for('main.profile', username=session["user"]))


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
@logged_in_user()
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

        curent_user = get_current_user()

        if not get_review:
            flash("Sorry we are unable to find that review", "danger")
            return redirect(url_for("main.profile", username=session["user"]))

        # Check whether the current user owns the review
        if ObjectId(get_review["user_id"]) == ObjectId(curent_user["_id"]):

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

        flash("You must be the review owner to edit", "warning")
        return redirect(request.referrer)

    return redirect(request.referrer)


@main.route("/review_delete/<review_id>", methods=["GET", "POST"])
@logged_in_user()
def review_delete(review_id):
    """
    Deletes a review based on the provided review_id.

    - For POST requests:
        * Deletes the review document from the MongoDB 'reviews' collection.
        * Retrieves the profile username from the submitted form data.
        * If the deletion is unsuccessful, flashes an error message and redirects to the profile page.
        * If the deletion is successful, flashes a success message and redirects to the profile page.
    - For non-POST requests, redirects to the home page.

    Args:
        review_id (str): The unique identifier of the review to be deleted.

    Returns:
        A Flask redirect response to either the user's profile page (after deletion) or the home page for GET requests.
    """
    if request.method == "POST":
        current_user = get_current_user()

        get_review_to_delete = mongo.db.reviews.find_one({
            "_id": ObjectId(review_id)
        })

        if ObjectId(current_user["_id"]) == ObjectId(get_review_to_delete["user_id"]):

            review_to_delete = mongo.db.reviews.delete_one({
                "_id": ObjectId(review_id)
            })

            profile_username = request.form.get("profile_username")

            if not review_to_delete:
                flash("Sorry something went wrong", "danger")
                return redirect(url_for('main.profile', username=profile_username))

            flash("Deleted Successfully!", "success")
            return redirect(url_for('main.profile', username=profile_username))

        flash("You must own the review to delete it", "warning")
        return redirect(request.referrer)

    return redirect(url_for("main.home"))


@main.route("/searched_category", methods=["GET", "POST"])
def searched_category():
    """
    Handles category-based business searches and redirects to user profiles.

    For POST requests:
    - Retrieves the owner_id from the form data.
    - Finds the user profile associated with the owner_id.
    - Extracts the username from the profile.
    - If the profile is not found, flashes an error and redirects to the home page.
    - If a user is logged in, flashes a welcome message and redirects to the user's profile.
    - If no user is logged in, flashes a warning and redirects to the login page.

    For GET requests:
    - Retrieves the selected category from the query parameters.
    - Queries the 'business' collection for all businesses that match the selected category.
    - If no businesses are found, flashes an error message and redirects to the home page.
    - If businesses are found, renders the 'searched_category.html' template with the category data.

    Args:
        None (relies on form data for POST requests and query parameters for GET requests).

    Returns:
        A Flask response object:
            - Redirects to the profile page, home page, or login page for POST requests.
            - Renders the 'searched_category.html' template with business data for GET requests.
    """
    if request.method == "POST":
        owner_id = request.form.get("owner_id")

        getProfile = mongo.db.users.find_one({
            "_id": ObjectId(owner_id)
        })

        username = getProfile["username"]

        if not getProfile:
            flash("Something went wrong", "danger")
            return redirect(url_for("main.home"))

        # Safely check if the user is logged in
        if "user" in session:
            flash(f"Welcome to {username}'s profile", "success")
            return redirect(url_for("main.profile", username=username))
        else:
            # Save the url/route the user is trying to view 
            session["next"] = url_for("main.profile", username=username)

            flash("Please log in to view profiles.", "warning")
            return redirect(url_for("main.login"))

    selected_category = request.args.get("category")

    category = list(mongo.db.business.find({
        "category": selected_category
    }))

    if not category:
        flash(f"""There are currently no businesses under
               {selected_category}""", "danger")
        return redirect(url_for("main.home"))

    return render_template("searched_category.html", category=category, selected_category=selected_category)


@main.route("/delete_business/<business_user_id>", methods=["GET", "POST"])
@logged_in_user()
def delete_business(business_user_id):
    """
    Handles the deletion of a business and its associated reviews.

    Process:
    - Retrieves the current logged-in user.
    - Fetches the business document using the provided business_user_id.
    - Ensures that the business exists; otherwise, flashes an error and redirects to the profile page.
    - Checks if the logged-in user is the owner of the business.
    - If the user is not authorized, flashes an error and redirects to the profile page.
    - If authorized:
        - Deletes the business from the database.
        - Deletes all reviews associated with the business.
        - Flashes a success message confirming the deletion.
    - If an error occurs during deletion, catches the exception, flashes an error, and redirects to the profile page.

    Args:
        business_user_id (str): The unique identifier of the business to be deleted.

    Returns:
        A Flask response object:
            - Redirects to the profile page after successful deletion.
            - Redirects to the profile page if the business is not found or if the user is unauthorized.
            - Redirects to the profile page if an error occurs during deletion.
    """
    current_user = get_current_user()

    business = get_business_owner(business_user_id)

    if not business:
        flash("Business not found", "danger")
        return redirect(url_for("main.profile", username=session["user"]))

    if current_user["_id"] != business["owner_id"]:
        flash("You are not authorized to delete this business", "danger")
        return redirect(url_for("main.profile", username=session["user"]))

    try:
        mongo.db.business.delete_one({"_id": ObjectId(business["_id"])})

        mongo.db.reviews.delete_many(
            {"business_id": ObjectId(business_user_id)})

        mongo.db.deals.delete_one({
            "business_owner": ObjectId(business_user_id)
        })

        flash("Business and associated reviews deleted successfully", "success")
    except Exception as e:
        flash(f"An error occurred: {e}", "danger")
        return redirect(url_for("main.profile", username=session["user"]))

    return redirect(url_for("main.profile", username=session['user']))


@main.route("/delete_account/<username>", methods=["GET", "POST"])
@logged_in_user()
def delete_account(username):
    """
    Handles user account deletion along with associated business and reviews.

    For POST requests:
    - Retrieves the current logged-in user and the profile being accessed.
    - Ensures that the user attempting to delete the account is its owner.
    - Checks if the user owns a business in the database.
    - If a business exists:
        - Deletes all reviews associated with the business.
        - Deletes the business itself from the database.
    - Deletes the user account from the database.
    - Clears the session to log out the user.
    - Flashes a success message and redirects to the home page.

    If the request is not a POST or the user is not the account owner:
    - Flashes a warning message and redirects to the profile page.

    Args:
        username (str): The username of the account being deleted.

    Returns:
        A Flask response object:
            - Redirects to the home page after successful account deletion.
            - Redirects to the profile page if the user is unauthorized.
    """
    if request.method == "POST":
        # Fetch the current user and the profile user
        current_user = get_current_user()
        page_profile_user = get_profile_user(username)

        # Check if the current user is the owner of the profile
        if page_profile_user["username"] == session["user"]:
            # Check for business owned by the user
            check_for_business = mongo.db.business.find_one({
                "owner_id": ObjectId(current_user["_id"])
            })

            # If a business exists, delete all associated reviews
            if check_for_business:
                mongo.db.reviews.delete_many({
                    "business_id": ObjectId(check_for_business["owner_id"])
                })

                # Delete the business itself
                mongo.db.business.delete_one({
                    "_id": ObjectId(check_for_business["_id"])
                })

            # Delete the user account
            mongo.db.users.delete_one({
                "_id": ObjectId(current_user["_id"])
            })

            # Clear the session and redirect to home
            session.pop("user")
            flash("Account deleted successfully!", "success")
            return redirect(url_for("main.home"))

    # If the current user is not the owner of the profile
    flash(f"You must be the account owner to delete it.", "warning")
    return redirect(url_for("main.profile", username=session["user"]))


@main.route("/create_deal/<business_id>", methods=["GET", "POST"])
@logged_in_user()
def create_deal(business_id):
    """
    Handles the creation of a new business deal.

    For POST requests:
    - Retrieves the current logged-in user.
    - Checks if the current user is the owner of the specified business.
    - If the user is not the owner, flashes an error message and redirects to their profile.
    - Ensures an image file is uploaded; otherwise, flashes an error message and reloads the page.
    - Reads and encodes the uploaded image into Base64 format.
    - Collects deal information from the form, including:
        - Business owner ID
        - Deal description (deal-text)
        - Start and expiration dates
        - Encoded deal image
    - Inserts the deal into the database.
    - If insertion fails, flashes an error message and redirects to the profile page.
    - On success, flashes a confirmation message and reloads the current page.

    For GET requests:
    - Redirects the user to their profile page, as deal creation should only be a POST action.

    Args:
        business_id (str): The unique identifier of the business creating the deal.

    Returns:
        A Flask response object:
            - Redirects to the user's profile if they are not the business owner.
            - Reloads the current page if an image is missing or a database insertion fails.
            - Displays a success message and reloads the page on successful deal creation.
            - Redirects to the profile page for unauthorized access attempts.
    """
    if request.method == "POST":
        # check the person creating is the account owner
        current_user = get_current_user()
        business_owner = get_business_owner(ObjectId(business_id))

        # check whether user owns account
        if current_user['_id'] == business_owner['owner_id']:

            if "deal-image" not in request.files or not request.files["deal-image"].filename:
                flash("No image uploaded", "danger")
                return redirect(request.url)

            # Get file
            file = request.files["deal-image"]

            if file:  # Ensure the file is not empty
                # Read image content
                image_content = file.read()
                # Encode image to Base64
                encoded_image = base64.b64encode(image_content).decode("utf-8")

                # You can now store or use the encoded_image as needed
                # For example: save to database or pass to template

                create = {
                    "business_owner": ObjectId(business_id),
                    "deal-text": request.form.get("deal-text"),
                    "date": request.form.get("date"),
                    "expire-date": request.form.get("expire-date"),
                    "deal-image": encoded_image
                }

                upload_deal = mongo.db.deals.insert_one(create)

                if not upload_deal:
                    flash(
                        "WOW, we are very sorry but something has gone wrong", "warning")
                    return redirect(url_for("main.profile", username=session["user"]))

                flash("Deal Created!!", "success")
                return redirect(request.full_path)

        flash("You must be the owner of the business to create a deal", "danger")
        return redirect(url_for("main.profile", username=session["user"]))

    return redirect(url_for("main.profile", username=session['user']))


@main.route("/deals", methods=["GET", "POST"])
def deals():
    """
    Handles business deal retrieval and user profile redirection.

    For POST requests:
    - Ensures the user is logged in before processing.
    - Retrieves the user_id from the form data.
    - Attempts to find the corresponding user profile in the database.
    - If the profile exists, redirects the user to their profile page.
    - If the profile is not found, flashes an error message and reloads the page.
    - If the provided user_id is invalid, flashes an error message and reloads the page.
    - If the user is not logged in, redirects to the login page.

    For GET requests:
    - Fetches all available deals from the 'deals' collection in the database.
    - Converts the query results into a list.
    - Renders the 'deals.html' template, passing the retrieved deals.

    Args:
        None (relies on session data and form input for POST requests).

    Returns:
        A Flask response object:
            - Redirects to the user's profile page if found (POST request).
            - Reloads the current page if an error occurs (POST request).
            - Redirects to the login page if the user is not logged in (POST request).
            - Renders the 'deals.html' template with retrieved deals (GET request).
    """
    if request.method == "POST":
        if "user" in session:
            user_id = request.form.get("user_id")

            if user_id:
                try:
                    profile_user = mongo.db.users.find_one(
                        {"_id": ObjectId(user_id)})

                    if profile_user:
                        return redirect(url_for("main.profile", username=profile_user["username"]))
                    else:
                        flash(
                            "Oops! We couldn't find that profile. Please try again.", "danger")
                        return redirect(redirect.url)

                except Exception:
                    flash("Invalid user ID format.", "danger")
                    return redirect(request.url)

            return redirect(request.url)

        flash("You must be logged in to see profiles", "warning")
        return redirect(url_for("main.login"))

    return render_template("deals.html", deals=list(mongo.db.deals.find()))


@main.route("/edit_promo/<edit_id>", methods=["GET", "POST"])
@logged_in_user()
def edit_promo(edit_id):
    """
    Allows users to edit a promo, including updating text, expiration date, and image.

    GET request:
        - Fetches the current promo details from the database to display in the edit form.

    POST request:
        - Updates the existing promo in the database with new details from the form.
        - If an image is uploaded, replaces the old image; otherwise, retains the existing image.
        - If the promo does not exist, flashes an error message.
        - If the update is unsuccessful, flashes an error message.

    Args:
        edit_id (str): The unique identifier (_id) of the promo to be edited.

    Returns:
        - On success: Redirects back to the referring page with a success message.
        - On failure: Redirects back to the referring page with an error message.
    """
    if request.method == "POST":
        get_promo = mongo.db.deals.find_one({"_id": ObjectId(edit_id)})

        if not get_promo:
            flash("Sorry, we cannot find that promo", "danger")
            return redirect(request.referrer)

        current_user = get_current_user()

        if ObjectId(get_promo["business_owner"]) == ObjectId(current_user["_id"]):

            image_data = getImages("deal-image")

            # Prepare update data
            updated_promo = {
                "deal-text": request.form.get("deal-text"),
                "expire-date": request.form.get("expire-date"),
                "deal-image": image_data if image_data else get_promo['deal-image']
            }

            # Perform the update in MongoDB
            update = mongo.db.deals.update_one(
                {"_id": ObjectId(edit_id)},
                {"$set": updated_promo}
            )

            if not update:
                flash("Sorry something has gone wrong", "danger")
                return redirect(request.referrer)

            flash("You have successfully updated your promo", "success")
            return redirect(request.referrer)

        flash("You must be the business owner to edit the deal", "warning")
        return redirect(request.referrer)


@main.route("/deal_delete/<delete_id>", methods=["GET", "POST"])
@logged_in_user()
def deal_delete(delete_id):
    """
    Deletes a specific deal from the database.

    GET request:
        - Typically, this endpoint should not process a GET request.
        - A GET request to this route does nothing unless explicitly handled elsewhere.

    POST request:
        - Deletes the deal from the database using its unique ID.
        - If the deletion is unsuccessful, flashes an error message.
        - If successful, flashes a confirmation message and redirects.

    Args:
        delete_id (str): The unique identifier (_id) of the deal to be deleted.

    Returns:
        - On success: Redirects back to the referring page with a success message.
        - On failure: Redirects back to the referring page with an error message.
    """
    if request.method == "POST":
        current_user = get_current_user()

        get_promo = mongo.db.deals.find_one({"_id": ObjectId(delete_id)})

        if ObjectId(get_promo["business_owner"]) == ObjectId(current_user["_id"]):

            delete_deal = mongo.db.deals.delete_one({
                "_id": ObjectId(delete_id)
            })

            if not delete_deal:
                flash("How embarressing, Something has gone wrong", "warning")
                return redirect(request.referrer)

            flash("Successfully deleted", "success")
            return redirect(request.referrer)

        flash("You must be business owner to delete promo", "warning")
        return redirect(request.referrer)
