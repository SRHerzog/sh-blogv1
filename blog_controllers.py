"""
Controller classes for fetching, creating, and rendering blog posts.

Exports classes:

Handler(webapp2.RequestHandler)
Generic handler class extended by specific controllers

MLStripper
Strips HTML tags from strings

MainPage(Handler)
Renders main page

BlogPost(Handler)
Renders individual blog posts

WritePost(Handler)
Renders post entry form and saves new posts to database

EditPost(Handler)
Renders post entry form for editing and saves edits
"""

# Auto formatted with Sublime text plugin
# HTML tag strip class and function from
# http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python

import webapp2
import jinja2
import models
import os
from Crypto.Hash import SHA256
from HTMLParser import HTMLParser
from secrets import Secret
from google.appengine.ext import db


class Handler(webapp2.RequestHandler):
    """ Generic handler class extended by specific controllers

    write:
        shorthand for response.out.write
    render_str(self, template, **params):
        shorthand for jinja_env.get_template(template).render(params)
    render(self, tamplate, **kw):
        shorthand view rendering function
    validate_cookie:
        checks username and hashed value from cookie
        deletes cookie if not matched
    strip_tags(self, html):
        returns a string with html tags removed
    """
    template_dir = os.path.join(os.path.dirname(__file__), 'templates')
    jinja_env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(template_dir),
        autoescape=False)

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = self.jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

    def validate_cookie(self):
        name = self.request.cookies.get("user")
        cookie_hash = self.request.cookies.get("auth")
        if name and cookie_hash:
            if cookie_hash == SHA256.new(name +
                                         Secret.cookie_secret).hexdigest():
                return True
        else:
            self.response.delete_cookie("user")
            self.response.delete_cookie("auth")
            return False

    def strip_tags(self, html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()


class MLStripper(HTMLParser):
    """ Utility class for stripping HTML tags from strings

    handle_data
        accepts data and appends it to a list self.fed
    get_data
        returns self.fed as a joined string
    """

    def __init__(self):
        self.reset()
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)


class MainPage(Handler):
    """ Serves "/" route and renders index.html
        Sets cookies on successful authentication
    """

    def get(self):
        message = self.request.get("message")
        error = self.request.get("error")
        if self.validate_cookie():
            username = self.request.cookies.get("user")
        else:
            username = self.request.get("username")
            auth = self.request.get("auth")
            # Cookie hash is created by user controller and passed to main page
            if auth:
                self.response.set_cookie(
                    key="auth",
                    value=auth,
                    path='/',
                    domain='localhost',
                    secure=False)
                self.response.set_cookie(
                    key="user",
                    value=username,
                    path='/',
                    domain='localhost',
                    secure=False)
        # Retrieve up to 5 posts from the database
        offset = self.request.get("offset")
        if offset:
            offset = int(offset)
        else:
            offset = 0
        posts = db.GqlQuery(
            "SELECT * FROM Post ORDER BY created DESC"
            ).run(limit=5, offset=offset)
        # Determine whether there are enough remaining posts to include
        # an "older" link on the page
        count = db.GqlQuery(
            "SELECT * FROM Post ORDER BY created DESC"
            ).count(limit=6, offset=offset)
        self.render("index.html",
                    posts=posts,
                    count=count,
                    message=message,
                    error=error,
                    user=username,
                    offset=offset)


class ReadPost(Handler):
    """ Serves "/p/*" route and renders individual posts """

    def get(self, *a, **kw):
        own_post = False
        post_id = kw['post']
        post = models.Post.get_by_id(int(post_id))
        if not post:
            self.write("No such post! It may have been deleted."
                       "<a href='/'>Return to the index.</a>")
            return
        q = db.Query(models.Comment).ancestor(post).order('-created')
        comments = q.run()
        username = self.request.cookies.get("user")
        if (self.validate_cookie() and
                username == post.author):
            own_post = True
        url = webapp2.RequestHandler.uri_for(self, 'post', post=post_id)
        self.render("singlepost.html",
                    p=post,
                    url=url,
                    own_post=own_post,
                    comments=comments,
                    user=username)


class WritePost(Handler):
    """ Serves "/new" route and renders new post form """

    def get(self, *a, **kw):
        # Display form
        if not self.validate_cookie():
            self.redirect("/#login")
        else:
            username = self.request.cookies.get("user")
            self.render("new.html", action="new", user=username)

    def post(self):
        # Validate data and save post to database
        if not self.validate_cookie():
            self.redirect("/login")
        else:
            username = self.request.cookies.get("user")
            title = self.request.get("title")
            text = self.request.get("content")
            # Format text for appropriate display
            # Remove all tags and then replace newlines with <br /> tags
            text = self.strip_tags(text)
            text = text.replace('\n', '<br />')
            if not (title and text):
                self.render("new.html",
                            author=username,
                            title=title,
                            text=text,
                            action=new,
                            message="Title and Text fields are required.")
            else:
                new_post = models.Post(author=username, title=title, text=text)
                new_post.put()
                self.redirect("/")


class EditPost(Handler):
    """ Serves "/edit" route and renders edit post form """

    def get(self):
        if not self.validate_cookie():
            self.redirect("/login")
        else:
            username = self.request.cookies.get("user")
            post_id = self.request.get("id")
            post = models.Post.get_by_id(int(post_id))
            # Reformat text from page display to textarea display
            text = post.text.replace('<br />', '\n')
            if username != post.author:
                message = "Authentication error. Please log in again."
                self.redirect("/?message=" + message)
            else:
                self.render("new.html",
                            message="Editing post.",
                            author=post.author,
                            title=post.title,
                            text=text,
                            action="edit",
                            id=post_id)

    def post(self):
        username = self.request.cookies.get("user")
        post_id = self.request.get("id")
        existing_post = models.Post.get_by_id(int(post_id))
        if not existing_post.author == username:
            message = ("Authentication error. Unable to edit post"
                       "written by {0}. If you are {0}, notify admin.")
            self.render("new.html",
                        action="new",
                        author=username,
                        title=title,
                        text=text,
                        message=message.format(existing_post.author))
        else:
            title = self.request.get("title")
            text = self.request.get("content")
            # Format text for appropriate display
            # Remove all tags and then replace newlines with <br /> tags
            text = self.strip_tags(text)
            text = text.replace('\n', '<br />')
            existing_post.title = title
            existing_post.text = text
            existing_post.put()
            self.redirect(str("p/" + post_id))


class DeletePost(Handler):
    """ Deletes posts """

    def get(self):
        self.redirect("/")

    def post(self):
        post_id = self.request.get("id")
        post = models.Post.get_by_id(int(post_id))
        username = self.request.cookies.get("user")
        if not (self.validate_cookie() and username == post.author):
            message = ("Authentication error. Unable to delete post"
                       "written by {0}. If you are {0}, notify admin.")
            self.render("/p/" + post_id, message=message)
        else:
            db.delete(post)
            self.redirect("/?message=Post deleted.")
