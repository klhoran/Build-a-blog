#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import webapp2
import os
import jinja2

from google.appengine.ext import db

template_dir = os.path.join(os.path.dirname(__file__), "templates")
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir), autoescape = True)



class BlogHandler(webapp2.RequestHandler):
    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)

    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    def render(self, template, **kw):
        self.write(self.render_str(template, **kw))

class BlogPost(db.Model):
    title = db.StringProperty(required = True)
    thoughts = db.TextProperty(required = True)
    created = db.DateTimeProperty(auto_now_add = True)

class BlogMain(BlogHandler):
    def get(self):
        bposts = db.GqlQuery("SELECT * FROM BlogPost ORDER BY created Desc LIMIT 5")
        self.render("blog_main.html", bposts = bposts)


class AddPost(BlogHandler):

    def render_addpost(self, title="", thoughts="", error=""):

        self.render("add_blog.html", title = title, thoughts = thoughts, error = error)

    def get(self):
        self.render_addpost()

    def post(self):
        title = self.request.get("title")
        thoughts = self.request.get("thoughts")

        if title and thoughts:
            bp = BlogPost(title = title, thoughts = thoughts)
            bp.put()

            self.redirect('/blog/' + str(bp.key().id()))
        else:
            error = "Both Title and Thoughts must be filled in"
            self.render_addpost(title, thoughts, error)

class ViewPostHandler(webapp2.RequestHandler):
    def get(self, id):
        post = BlogPost.get_by_id(int(id))
        if post:
            t = jinja_env.get_template("single_post.html")
            content = t.render(post = post)
            self.response.write(content)
        else:
            self.respone.write("No such blog entry")




app = webapp2.WSGIApplication([

    ('/blog', BlogMain),
    ('/blog/', BlogMain),
    ('/blog/newpost', AddPost),
    ('/blog/newpost/', AddPost),
    webapp2.Route('/blog/<id:\d+>', ViewPostHandler)

], debug=True)
