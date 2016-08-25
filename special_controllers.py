"""
Controller classes for special functions.
Currently only includes "likes" and the 404 handler.

Exports classes:

Like

Unlike

NotFound
Redirects all unknown URLs to "/"
"""

import models
import os
from blog_controllers import Handler
from google.appengine.ext import db


class Like(Handler):
    """ Adds logged-in user's name to the likes list for a given post """

    def get(self):
        self.redirect("/")

    def post(self):
        message = ""
        if not self.validate_cookie():
            self.redirect("/")
            return
        username = self.request.cookies.get("user")
        post_id = self.request.get("post_id")
        post = models.Post.get_by_id(int(post_id))
        if username == post.author:
            message = ("You can't like your own posts."
                       "This is a bug. Please notify admin.")
        else:
            post.likes.append(username)
            post.put()
            message = ("Success! <a href='/p/" + post_id + "'>Return</a>")
        self.write(message)


class Unlike(Handler):
    """ Removes logged-in user's name from the post likes list """

    def get(self):
        self.redirect("/")

    def post(self):
        message = ""
        if not self.validate_cookie():
            self.redirect("/")
            return
        username = self.request.cookies.get("user")
        post_id = self.request.get("post_id")
        post = models.Post.get_by_id(int(post_id))
        if username not in post.likes:
            message = ("! The site doesn't think you can unlike this."
                       "This is a bug. Please notify admin.")
        else:
            post.likes.remove(username)
            post.put()
            message = ("Success! <a href='/p/" + post_id + "'>Return</a>")
        self.write(message)


class NotFound(Handler):
    """ Catch all invalid URLs and redirect to index """

    def get(self):
        self.redirect("/")
