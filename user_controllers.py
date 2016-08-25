"""
Controller classes for user authentication functions (register, login, logout).

Exports classes:

Register(Handler)
	Renders registration form and handles new user registration.

Login(Handler)
	Renders login form and authenticates users.

Logout(Handler)
	Deletes login cookies and redirects to main page.
"""

# Auto formatted with Sublime text plugin

import models
from Crypto.Hash import SHA256
from secrets import Secret
from blog_controllers import Handler
import datetime

class Register(Handler):

    def get(self):
        # Redirect to index registration form if browser requests "/register"
        self.redirect("/#register")

    def post(self):
        name = self.request.get("name")
        raw_pass = self.request.get("password")
        if name and len(raw_pass) > 5:
            # Check for existing user. If none found, proceed with registration
            u = models.User.get_by_key_name(name)
            if not u:
                password = SHA256.new(
                    raw_pass + Secret.local_auth_secret).hexdigest()
                new_user = models.User(
                    key_name=name, name=name, pass_hash=password)
                new_user.put()
                message = "Registration successful!"
                auth = SHA256.new(name + Secret.cookie_secret).hexdigest()
                redirect = "/?message={0}&username={1}&auth={2}"
                self.redirect(redirect.format(message, name, auth))
            else:
                error = ("Username already exists.%0A"
                         "Log in or choose a different name.")
                self.redirect("/?error=" + error + "#register")
        elif len(raw_pass) <= 5:
            message = "Password must be six characters or longer."
            self.redirect("/?error=" + message + "#register")
        else:
            error = ("Registration error.%0A"
                     "Please re-enter your registration and try again.")
            self.redirect("/#login?error=" + error + "#register")


class Login(Handler):

    def get(self):
        self.redirect("/#login")

    def post(self):
        message = ""
        name = self.request.get("name")
        raw_pass = self.request.get("password")
        if name and raw_pass:
            u = models.User.get_by_key_name(name)
            if not u:
                error = ("Username not found.%0ACheck the spelling or "
                         "create a new account.")
                self.redirect("/?error=" + error + "#login")
            else:
                password = SHA256.new(
                    raw_pass + Secret.local_auth_secret).hexdigest()
                if password != u.pass_hash:
                    error = ("Invalid password.%0A"
                             "Retype your password and try again.")
                    self.redirect("/?error=" + error + "#login")
                else:
                    message = "Welcome back!"
                    auth = SHA256.new(name + Secret.cookie_secret).hexdigest()
                    self.redirect("/?message={0}&username={1}&auth={2}"
                                  .format(message, name, auth))


class Logout(Handler):

    def get(self):
        self.response.set_cookie(
            key="auth",
            value="",
            path='/',
            secure=True,
            expires=datetime.datetime.fromtimestamp(0))
        self.response.set_cookie(
            key="user",
            value="",
            path='/',
            secure=True,
            expires=datetime.datetime.fromtimestamp(0))
        message = "Logged out."
        self.redirect("/?message=" + message)
