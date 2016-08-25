"""
Entry point for app.yaml and routing table for multi-user blog application.
"""

# Auto formatted with Sublime Text plugin

import webapp2
import os
import blog_controllers as blog
import user_controllers as auth
import comment_controller as comments
import special_controllers as special

app = webapp2.WSGIApplication([
    ('/', blog.MainPage),
    webapp2.Route(r'/p/<post>', blog.ReadPost, name='post'),
    ('/edit', blog.EditPost),
    ('/new', blog.WritePost),
    ('/delete', blog.DeletePost),
    ('/newcomment', comments.PostComment),
    ('/editcomment', comments.EditComment),
    ('/deletecomment', comments.DeleteComment),
    ('/register', auth.Register),
    ('/login', auth.Login),
    ('/logout', auth.Logout),
    ('/like', special.Like),
    ('/unlike', special.Unlike),
    ('/.*', special.NotFound)
], debug=True)
