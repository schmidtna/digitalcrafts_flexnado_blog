#!/usr/bin/env python3

import os
import tornado.ioloop
import tornado.web
import tornado.log
import queries

from jinja2 import \
  Environment, PackageLoader, select_autoescape

ENV = Environment(
  loader=PackageLoader('blog', 'templates'),
  autoescape=select_autoescape(['html', 'xml'])
)

class TemplateHandler(tornado.web.RequestHandler):
  def initialize(self):
    self.session = queries.Session(
      'postgresql://postgres@localhost:5432/blog_exercise')

  def render_template (self, tpl, context):
    template = ENV.get_template(tpl)
    self.write(template.render(**context))

class MainHandler(TemplateHandler):
  def get (self):
    posts = self.session.query('SELECT * FROM post')
    self.render_template("home.html", { 'posts': posts })

class BlogPostHandler(TemplateHandler):
  def get (self, slug):
    posts = self.session.query(
      'SELECT * FROM post WHERE slug = %(slug)s',
      {'slug': slug}
    )
    self.render_template("post.html", {'post': posts[0]})
    





def make_app():
  return tornado.web.Application([
    (r"/", MainHandler),
    (r"/post/(.*)", BlogPostHandler),
    (r"/static/(.*)", 
      tornado.web.StaticFileHandler, {'path': 'static'}),
  ], autoreload=True)


if __name__ == "__main__":
  tornado.log.enable_pretty_logging()
  app = make_app()
  app.listen(int(os.environ.get('PORT', '8080')))
  tornado.ioloop.IOLoop.current().start()