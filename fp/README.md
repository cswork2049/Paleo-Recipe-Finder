# Paleo Recipe Finder :poultry_leg::meat_on_bone:

### Video Demo: https://www.youtube.com/watch?v=yvhdFkytXWM

### Description:
I created this app because I wanted an easy and fun way to get new paleo recipes (and also because I eventually
want a job as a web developer). This app allows me to search for or randomly find recipes, scraped from a website
containing them.

There is quite a bit of cooking involved in Paleo since it stresses whole, organic foods as its main staple,
and disregards processed and fast food; I felt that this would be a useful tool for my (mostly) daily cooking.

I've already used the tool to great effect!

### Project Files:
The following is a summary overview of all files. All files contain copious comments.
Please refer to a specific file for implementation and details.

##### application.py
This is the main application file that our API/web framework, Flask, will run from. We too use this file to interact with our
HTML files via Jinja. We also use it to program our user SQL database. It contains all of the backend, SQLite database code,
a helper function, a Recipe object class, and the `GET` and `POST` functionality behind our HTML.

##### helpers.py
This is a helper file to `application.py`. It assists the code that came with the CS50 distribution code. All functions in
this file are required for the application to run even if I am only using one of the functions contained therein
(`login_required(f)`).

##### finder.db
This is the database that stores our user information. We can read from and write to it via `application.py` when a user wants
to log in or register.

##### drumstick.ico
This is the favicon (a chicken drumstick) for our website.

##### Paleo Food.png
This is the background image for every page on the site.

##### styles.css
This styles the HTML further.

##### apology.html
This really should be called `homepage.html`. It's called `apology.html` because the distribution code of CS50 Finance
(PSET 8) seems to make it necessary (the index page needs to be called `apology.html` for some reason). It displays a
welcome page with options to log in or register.

##### apology_login.html
This is an actual apology that displays an alert to the user if they incorrectly enter login information.

##### apology_register.html
This is an actual apology that displays an alert to the user if they incorrectly enter registration information.

##### find_results.html
This page displays recipe results after the user logs in and hits the "Get a random recipe!" button in the navbar.
It shows the recipe title, clickable image, and summary, all scraped from the
[website](https://ultimatepaleoguide.com/recipes/#500+_Recipes_Counting!).

I went through several iterations of design before landing on this most simple one.

##### layout.html
This is the page that all other pages rely on for their general look and scheme. It contains a Bootswatch theme,
[Sketchy](https://bootswatch.com/sketchy/), which I thoroughly enjoy, as well as some JavaScript for user alerts,
and a neat footer.

##### login.html
This is the user login page.

##### my_recipes.html
This is a page for a function (`save()`) I decided not to implement, wherein the user could save recipes to our
database to refer back to them later. Due to time constraints, I decided not to pursue it at this time, though I
know doing so would involve Python pickling or ORM (Object-Relational Mapping). I've looked into SQLAlchemy.

##### register.html
This is the user registration page.

##### search_apology.html
This is an alert rendered to the user if no recipes are found matching their search or if they search without entering
any text.

##### search_results.html
This is a page displaying all of the recipes matched to a user's search terms. It is a group of cards displaying chosen
recipe attributes (recipe title, image and link, summary) in a grid. I played around with different card schemes for
this one (including decks), but liked how groups displayed the most.