# Paleo Recipe Finder
# It's a Flask application built with Python, SQL, HTML, CSS, Jinja, and JavaScript.

# This website utilizes, in part, the distribution code for PSET 8 Finance, provided by
# CS50 2020 (with permission). See: https://cs50.harvard.edu/x/2020/project/

# Use IEX API key to run the website locally from the console:
# In console:
# export API_KEY=pk_4c6df35359924235aa350943a92e1eb8
# --> flask run

import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Alex's imports:

# requests is used to get the HTML from a given URL.
import requests
# Beautiful Soup is a tool that allows one to parse and manipulate HTML (and other markup languages) content more easily.
from bs4 import BeautifulSoup
# Randomizes our list of recipes for the /find function.
import random

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finder.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")

def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

############################################
########## MY FUNCTIONS & CLASSES ##########
############################################

# A class that creates a recipe object (recipe title, URL link, image, summary).
class Recipe:
    def __init__(self, title, link, image):
        self.title = title
        self.link = link
        self.image = image
        self.summary = None

    def get_title(self):
        return self.title

    def get_link(self):
        return str(self.link)

    def get_image(self):
        return str(self.image)

    def get_summary(self):
        return str(self.summary)


# A function to determine if a searched word matches with a word in the title of recipes browsed:
# (found here: https://stackoverflow.com/questions/14352621/compare-if-an-element-exists-in-two-lists)
def word_match(search_terms, title_terms):
    for word in search_terms:
        if word in title_terms:
            return True
        else:
            return False


# A function that gets a random recipe for the user from a recipe website at the click of a button.
# No login required.
@app.route("/find")
def find():
    # Create a list to store recipe objects.
    recipe_list = []

    # Get the HTML from our URL.
    all_recipes_URL = 'https://ultimatepaleoguide.com/recipes/'
    html = requests.get(all_recipes_URL)

    # Use Beautiful Soup to make manipulating the HTML easier.
    parsed_html = BeautifulSoup(html.content, 'html.parser')

    # The section of the website that contains all of the recipes.
    container = parsed_html.find(id='wpupg-grid-all-recipes')

    # Get the recipes (anything with an 'a' (anchor) tag) within all_recipes.
    recipes = container.find_all('a')

    # Get only the link, the image, and the title from each recipe (item).
    for item in recipes:
        title = item.find('div', class_='wpupg-item-title wpupg-block-text-bold')
        link = item.get('href')
        image_div = item.find('div', class_='wpupg-item-image wpupg-block-image-normal wpupg-align-center')
        image = image_div.find('img').attrs['src']

        # Create a recipe object and add all three attributes to the object.
        recipe = Recipe(title, link, image)
        # Add the recipe object to a list.
        recipe_list.append(recipe)

    # Pick a random recipe from the list of recipes.
    random_recipe = random.choice(recipe_list)

    # Get the attributes from the random recipe as strings.
    title = random_recipe.get_title()
    # Call .text on the title so it displays to the user without HTML.
    title = title.text
    link = random_recipe.get_link()
    image = random_recipe.get_image()

    # Now, separately, take the steps to get the summary.
    # Get the random recipe summary from the link URL.
    recipe_link_html = requests.get(link)

    # Use Beautiful Soup again to make manipulating the summary HTML easier.
    parsed_html = BeautifulSoup(recipe_link_html.content, 'html.parser')

    # At least one of the recipes in our gotten recipes is not actually a recipe, but a list
    # that follows a different HTML format without a summary section, so if we encounter it we'll simply skip it
    # by running /find again (getting a new random recipe) to avoid an error being thrown.
    if parsed_html.find('div', class_='wprm-recipe wprm-recipe-simple') is not None:
        container = parsed_html.find('div', class_='wprm-recipe wprm-recipe-simple')
        summary = container.find('div', class_='wprm-recipe-summary')
        summary = summary.text
    else:
        return find()

    # Return the recipe to the user as a card displaying the recipe and its attributes.
    return render_template("find_results.html", title=title, link=link, image=image, summary=summary)


# A function that allows a user to search within our collection of recipes using keywords.
# No login required.
@app.route("/search", methods=["GET", "POST"])
def search():
    # Create a list to store matched recipe objects.
    recipe_list = []

    # Get search terms queried by user.
    search_terms = request.form.get("search_terms")
    # Ensure the user entered some text to search. If not, return an alert.
    if not request.form.get("search_terms"):
        error_code = "403"
        message = "Please enter some text for your search."
        return render_template("search_apology.html", error_code=error_code, message=message)

    # If they entered text, parse the search string by spaces, into a list. We will also make browsed recipe titles
    # lowercased, so when we compare searched terms with the title of recipes (title_terms), we won't have to worry about
    # whether the user inputted lower or uppercase letters in their search.
    search_terms = search_terms.lower().split(' ')
    # Find the recipe title section of all recipes in the All Recipes section of the website.
    # Get the HTML from our URL.
    all_recipes_URL = 'https://ultimatepaleoguide.com/recipes/'
    html = requests.get(all_recipes_URL)

    # Use Beautiful Soup to make manipulating the HTML easier.
    parsed_html = BeautifulSoup(html.content, 'html.parser')

    # The section of the website that contains all of the recipes.
    container = parsed_html.find(id='wpupg-grid-all-recipes')

    # Get the recipes (anything with an 'a' (anchor) tag) within all_recipes.
    recipes = container.find_all('a')

    # Get the attributes necessary to display to the user.
    # Check recipes list to see if any of our keywords from search_terms list are found in the titles in the recipes list.
    # We are approximating this search, not aiming for extreme specificity. One ingredient found in the search terms
    # will do for this purpose.
    for item in recipes:
        title = item.find('div', class_='wpupg-item-title wpupg-block-text-bold')
        # We will use "title" to display the title to the user with proper capitalization.
        title = title.text
        # Use "title_lower" to compare with search terms only.
        title_lower = title.lower()
        link = item.get('href')
        image_div = item.find('div', class_='wpupg-item-image wpupg-block-image-normal wpupg-align-center')
        image = image_div.find('img').attrs['src']

        # Parse the title words into a list, separating words by spaces.
        title_terms = title_lower.split(' ')
        # Compare title words with search words. If the word is found in both lists,
        # that means we have a recipe that includes an ingredient the user searched
        # for, so we'll return True from word_match().
        match = word_match(search_terms, title_terms)

        if match:
            # Create a recipe object for our matched recipe and add all three recipe attributes to the object.
            recipe = Recipe(title, link, image)
            # Add the matched recipe object to a list of matched recipes.
            recipe_list.append(recipe)

    # Get the summary of each recipe matched.
    for item in recipe_list:
        link = item.get_link()

        # Get the recipe summary from the link URL.
        recipe_link_html = requests.get(link)

        # Use Beautiful Soup to make manipulating the HTML easier.
        parsed_html = BeautifulSoup(recipe_link_html.content, 'html.parser')

        # Get the summary of each recipe.
        if parsed_html.find('div', class_='wprm-recipe wprm-recipe-simple') is not None:
            container = parsed_html.find('div', class_='wprm-recipe wprm-recipe-simple')
            summary = container.find('div', class_='wprm-recipe-summary')
            summary = summary.text
        # We know that at least one of the returned recipes might be a list without a summary section, so we
        # give the user some text to avoid the application throwing an exception.
        else:
            summary = "This is a list of recipes, not a single recipe."

        # Set the summary attribute of our object to whatever the recipe's summary is. We do it this way instead of
        # adding the summary to the object at object creation (along with the title, link, image), because doing so
        # the other way would significantly increase running time; we'd have to run Beautiful Soup for every
        # every individual recipe's summary.
        setattr(item, 'summary', summary)

    # Check: If recipe_list is empty, that means we found no matched recipes, so return an apology to the user.
    if len(recipe_list) == 0:
        error_code = "403"
        message = "Sorry, none of the terms you entered matched any recipe."
        return render_template("search_apology.html", error_code=error_code, message=message)

    # Return the recipe list to search_results to make a group of cards with each of the list's recipe's attributes.
    return render_template("search_results.html", recipe_list=recipe_list )


# A function that returns the user to the home page.
@app.route("/apology")
def index():
    return render_template("apology.html")

# A function to log a user in.
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user id.
    session.clear()

    # User reached route via POST (as by submitting a form via POST).
    if request.method == "POST":

        # Ensure username was submitted.
        if not request.form.get("username"):
            error_code = "403"
            message = "Please enter a username."
            return render_template("apology_login.html", error_code=error_code, message=message)

        # Ensure password was submitted.
        elif not request.form.get("password"):
            error_code = "403"
            message = "Please enter a password."
            return render_template("apology_login.html", error_code=error_code, message=message)

        # Query database for username.
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct.
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            error_code = "403"
            message = "Password entered incorrectly or user does not exist."
            return render_template("apology_login.html", error_code=error_code, message=message)

        # Remember which user has logged in.
        session["user_id"] = rows[0]["id"]

        # Redirect user to a randomly found recipe after they log in.
        return redirect("/find")

    # User reached route via GET so send them to the login page.
    else:
        return render_template("login.html")


# A function to log a user out.
@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id.
    session.clear()

    # Redirect user to main page.
    return render_template("apology.html")


# A function to register a new user.
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    # They entered information into the register.html form fields and submitted that information.
    if request.method == "POST":

        # Query database for username to see if any rows in the database contain it.
        username_row = db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))

        # If the username field is left blank or the username already exists in the database, return apology.
        # if len(rows) == 1, that means we have already have a row that contains that username.
        if not request.form.get("username") or len(username_row) == 1:
            error_code = "403"
            message = "Username not entered or username already exists!"
            return render_template("apology_register.html", error_code=error_code, message=message)

        # If the password field is left blank or passwords and confirmations are not the same, return apology.
        if not request.form.get("password") or request.form.get("password") != request.form.get("confirmation"):
            error_code = "403"
            message = "Please provide password and confirmation!"
            return render_template("apology_register.html", error_code=error_code, message=message)
        else:
            # Assign username to a variable.
            username = request.form.get("username")
            # Assign password to a variable.
            password = request.form.get("password")
            # Check to make sure password contains special characters.
            if len(password) < 8:
                error_code = "403"
                message = "Please provide a password that is eight or more characters!"
                return render_template("apology_register.html", error_code=error_code, message=message)
            # Hash the user's password to make it secure.
            password_hash = generate_password_hash(request.form.get("password"))
            # Insert new user row into users table.
            db.execute("INSERT INTO users (username, hash) VALUES (:username, :password_hash)",
                       username=username, password_hash=password_hash)

            # Query database for username so we can automatically log them in post-registration.
            rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

            # Remember which user has logged to keep them logged in immediately after registering.
            session["user_id"] = rows[0]["id"]

            # Redirect user to /find when finished.
            return redirect("/find")
    # Otherwise, we have a GET request, so we send the user to the register page to register their information.
    else:
        return render_template("register.html")



# Potential future TODOs:

# A function that allows a user to save the recipes they find into their profile.
# Login is required.
# @app.route("/save")
# def save():
#     # If a user is not logged in, we display an alert saying they need to be logged in.
#     # Otherwise, if a user is logged in (recognize this through session id?), we will alert
#     # them that the the recipe was saved (and save it to the database for the user). When the user
#     # later clicks on their profile, they will be able to see cards (in the style of found.html)
#     # of all their recipes.

#     # If a user is logged in
#     if session.user_id:
#         # Save the recipe to the database for this user and alert them that it was saved.
#         # (A quick alert that dissolves after 1 second without the user having to do anything.)
#         return 0
#     # Don't save and alert the user that they must register or login to save a recipe.
#     else:
#         return 0

#     return 0


# A function that allows a user to browse within our collection of recipes.
# No login required.
# @app.route("/browse")
# def browse():
#     # Solution: would only have to implement a basic version of find() function here and return search_results.html template
#     # to the user for all recipes. Deciding not to implement for now because I like the current look and functionality
#     # without it.
#     return 0

# # A function that loads all recipes saved by a user when they are logged in.
# # Login is required.
# @app.route("/load")
# @login_required
# def load():
#     return render_template("my_recipes.html")