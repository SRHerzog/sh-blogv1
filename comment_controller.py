"""
Controller classes for fetching, creating, and rendering blog comments.

Exports classes:

PostComment

EditComment

DeleteComment
"""

# Auto formatted with Sublime Text plugin

import models
import os
from blog_controllers import Handler
from google.appengine.ext import db


class PostComment(Handler):
    """ Handles submission to "/newcomment" and posts to db """

    def get(self):
        self.redirect("/")

    def post(self):
        message = ""
        if not self.validate_cookie():
            self.redirect("/login")
        else:
            username = self.request.cookies.get("user")
            text = self.request.get("content")
            # Only post comments if the text field is not empty
            if text:
                js = self.request.get("js")
                text = self.strip_tags(text)
                # Format text for appropriate display
                # Remove all tags and then replace newlines with <br /> tags
                text = text.replace('\n', '<br />')
                post_id = self.request.get("parent")
                post = models.Post.get_by_id(int(post_id))
                new_comment = models.Comment(parent=post,
                                             author=username,
                                             text=text)
                new_comment.put()
                post.comment_count += 1
                post.put()
                # Retrieve id of new comment for AJAX function
                q = db.Query(models.Comment).ancestor(post)
                comment_id = q.run(limit=1).next().key().id()
                # If client is using JavaScript, return the id
                if js:
                    message = str(comment_id) + ' ' + username
                # If no JavaScript on client, return a human readable message
                else:
                    message = ("Success! Comment posted. <a href='p/" +
                               post_id + "'>Return to the post.</a>")
            else:
                message = ("! Comment field was empty. <a href='p/" +
                           post_id + "'>Go back and try again.</a>")
        self.write(message)


class EditComment(Handler):
    """ Handles submission to "/editcomment" and updates db
        Renders comment edit form if necessary
        Only expect get requests from a browser with no JavaScript
    """

    def get(self):
        if not self.validate_cookie():
            self.redirect("/")
            return
        comment_id = self.request.get("comment_id")
        parent_id = self.request.get("parent")
        parent = models.Post.get_by_id(int(parent_id))
        comment = models.Comment.get_by_id(int(comment_id), parent=parent)
        # Reformat text from page display to textarea display
        text = comment.text.replace('<br />', '\n')
        self.render('editcomment.html',
                    id=comment_id,
                    parent=parent_id,
                    text=comment.text)

    def post(self):
        if not self.validate_cookie():
            self.redirect("/")
            return
        username = self.request.cookies.get("user")
        text = self.request.get("content")
        # Format text for appropriate display
        # Remove all tags and then replace newlines with <br /> tags
        text = self.strip_tags(text)
        text = text.replace('\n', '<br />')
        comment_id = self.request.get("comment_id")
        parent_id = self.request.get("parent")
        parent = models.Post.get_by_id(int(parent_id))
        comment = models.Comment.get_by_id(int(comment_id), parent=parent)
        if username != comment.author:
            message = ("! You can't edit someone else's comment. "
                       "This is a bug. Please report it to admin.")
        else:
            comment.text = text
            comment.edited = True
            comment.put()
            message = ("Success! Comment edited. <a href='p/" +
                       parent_id + "'>Return to the post.</a>")
        self.write(message)


class DeleteComment(Handler):
    """ Deletes comments """

    def get(self):
        self.redirect("/")

    def post(self):
        if not self.validate_cookie():
            self.redirect("/")
            return
        username = self.request.cookies.get("user")
        comment_id = self.request.get("comment_id")
        parent_id = self.request.get("parent")
        parent = models.Post.get_by_id(int(parent_id))
        comment = models.Comment.get_by_id(int(comment_id), parent=parent)
        if username != comment.author:
            message = ("! You can't delete someone else's comment. "
                       "This is a bug. Please report it to admin.")
        elif parent and comment:
            db.delete(comment)
            parent.comment_count -= 1
            parent.put()
            message = ("Success! Comment deleted. <a href='p/" +
                       parent_id + "'>Return to the post.</a>")
        else:
            message = ("! Something went wrong." + comment_id + " "
                       "\n " + parent_id + "\n" + username)
        self.write(message)
