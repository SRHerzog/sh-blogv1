"""
Database models for multi-user blog.

Exports classes User, Post, and Comment that extend
google.appengine.ext.db.Model, with no class methods.
"""

# Auto formatted with Sublime Text plugin

from google.appengine.ext import db


class User(db.Model):
    name = db.StringProperty(required=True)
    pass_hash = db.StringProperty(required=True)


class Post(db.Model):
    title = db.StringProperty(required=True)
    author = db.StringProperty(required=True)
    text = db.TextProperty(required=True)
    tags = db.StringProperty()
    likes = db.StringListProperty(default=[])
    comment_count = db.IntegerProperty(default=0)
    created = db.DateTimeProperty(auto_now_add=True)


class Comment(db.Model):
    author = db.StringProperty(required=True)
    text = db.TextProperty(required=True)
    edited = db.BooleanProperty(default=False)
    edit_time = db.DateTimeProperty(auto_now=True)
    created = db.DateTimeProperty(auto_now_add=True)
