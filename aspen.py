"""
The Main App
"""
import sys, os
import web

# set path
app_path = os.path.dirname(__file__)
sys.path.append(app_path)

if app_path:
	os.chdir(app_path)
else:
	app_path = os.getcwd()

import settings
import models
from models import render
import admin
from utilities import mdrender,decrypt
web.config.debug = settings.DEBUG

# 500 internal server error
def internalerror():
	return web.internalerror(render.error())

# 404 Not Found
def notfound():
	return web.notfound(render.notfound())

# url mapping
mapping = (
	"/admin",admin.app,
	"/post/(.+)", "post",
	"/archives", "archives",
	"/tag/([1-9]\d*)", "tag",
	"/category/([1-9]\d*)", "category",
	"", "reindex",
	"/", "index",
)

# get user information for the app
#user = models.getUserInfo()

class reindex:
	def GET(self): raise web.seeother('/')

class index:
	def GET(self):
		user = models.getUserInfo()
		profile2html = mdrender.mdrender(user["profile"])
		user["profile"] = profile2html
		recentPosts = models.getRecentPosts()
		return render.index(user,recentPosts)

class post:
	def GET(self,name):
		post = models.getPostById(name)
		if post is None:
			return render.notfound()
		else:
			user = models.getUserInfo()
			return render.post(post,user['realname'])

class archives:
	def GET(self):
		allPosts = models.getAllPosts()
		tags = models.getAllTags()
		categories = models.getAllCategory()
		user = models.getUserInfo()
		return render.archives(allPosts,user['realname'],tags,categories)

class tag:
	def GET(self,tagid):
		posts = models.getPostByTag(int(tagid))
		if posts is None:
			return render.notfound()
		user = models.getUserInfo()
		return render.tag(posts,user['realname'])

class category:
	def GET(self,categoryid):
		posts = models.getPostByCategory(int(categoryid))
		if posts is None:
			return render.notfound()
		user = models.getUserInfo()
		return render.category(posts,user['realname'])

app = web.application(mapping,locals())

# when deploy the app, uncomment this line
#app.internalerror = internalerror
app.notfound = notfound
application = app.wsgifunc()

if __name__=="__main__":
	app.run()
