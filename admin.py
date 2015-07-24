"""
The admin App
"""
import os
import web
import settings
import models
from models import render

web.config.debug = settings.DEBUG

urls = (
	"/userinfo",'userinfo',
	"/postsadmin","postsadmin",
	"/edit/(.+)","edit",
	"/new","new",
	"/view/(.+)","view",
	"/delete/(.+)","delete",
	"/upload","upload",
	"/newpwd","newpwd",
	"","readmin",
	"/", "admin",
)

class readmin:
	def GET(self):
		raise web.seeother("/")

class admin:
	def GET(self):
		auth = {"error":1,"msg":"Please Sign In.","value":""}
		if session['login'] > 0:
			auth["error"] = 0
			auth["msg"] = None
			auth["value"] = session['user']
		return render.admin(auth)
	
	def POST(self):
		input_val=web.input()
		name = input_val['name']
		pwd = input_val['pwd']
		auth = models.userAuth(name,pwd)
		#assert False
		if auth['error'] ==0:
			session['login'] = 1
			session['user'] = auth['value']
		return render.admin(auth)

class userinfo:
	def GET(self):
		if session['login'] == 0:
			raise web.seeother('/')
		else:
			return render.userinfo(session['user'],None)

	def POST(self):
		if session['login'] == 0:
			raise web.seeother('/')
		else:
			input_val=web.input()
			user = models.updateUserInfo(input_val)
			#user = None
			if user is None:
				return render.userinfo(session['user'],"Error Occurs.")
			#input_val['pwd'] = session.user['pwd']
			session.user = user
			raise web.seeother('/userinfo')

class postsadmin:
	def GET(self):
		if session['login'] == 0:
			raise web.seeother('/')
		allPosts = models.getAllPosts(private=True)
		return render.postsadmin(session['user'],allPosts)

class new:
	def GET(self):
		if session['login'] == 0:
			raise web.seeother('/') 
		return render.edit(session['user'],None,None)
	
	def POST(self):
		if session['login'] == 0:
			raise web.seeother('/')
		post = web.input()
		post = models.preprocesspost(post)
		#post['type'] = int(post['type'])
		po = models.getPostById(post['title_id'],private=True,edit=True)
		if po is not None:
			return render.new(session['user'],post,'Try another Title ID.')
			#raise web.seeother('%s' % title_id)
		else:
			re = models.newPost(post)
			if re is True:
				raise web.seeother('edit/%s' % post['title_id'])
			else:
				return render.new(session['user'],post,'Error.')
class edit:
	def GET(self,title_id):
		if session['login'] == 0:
			raise web.seeother('/')
		else:
			post = models.getPostById(title_id,private=True,edit=True)
			return render.edit(session['user'],post,None)

	def POST(self,title_id):
		if session['login'] == 0:
			raise web.seeother('/')
		post = web.input()
		post = models.preprocesspost(post)
		#post['type'] = int(post['type'])
		po = models.getPostById(title_id,private=True,edit=True)
		re = models.updatePost(post,po)
		if re is True:
			raise web.seeother('/edit/%s' % title_id)
		else:
			return render.edit(session['user'],post,'Error.')

class view:
	def GET(self,title_id):
		if session['login'] == 0:
			raise web.seeother('/')
		post = models.getPostById(title_id,private=True)
		if post is None:
			return render.notfound()
		else:
			return render.preview(post)

class delete:
	def GET(self,title_id):
		if session['login'] == 0:
			raise web.seeother('/')
		models.deletePost(title_id)
		raise web.seeother('/postsadmin')


class upload:
	def GET(self):
		if session['login'] == 0:
			raise web.seeother('/')
		return render.upload(None)
	
	def POST(self):
		f = web.input(infile={})
		filedir = "static/upload"
		try:
			if 'infile' in f:
				filepath=f.infile.filename.replace('\\','/') 
				filename=filepath.split('/')[-1] 
				fout = open(filedir +'/'+ filename,'w')
				fout.write(f.infile.file.read()) 
				fout.close() 
				msg = "Success Upload file %s" % filename
				return render.upload(msg)
		except:
			msg = "Error Occurs."
			return render.upload(msg)

class newpwd:
	def GET(self):
		if session['login'] == 0:
			raise web.seeother('/')
		return render.pwd(None)
	def POST(self):
		pwds = web.input()
		if pwds['pwd1'] != pwds['pwd2']:
			msg = "Entered passwords differ"
			return render.pwd(msg)
		else:
			models.setnewpwd(pwds['pwd1'])
			user = session['user']
			auth = models.userAuth(user['username'],pwds['pwd1'])
			if auth['error'] ==0:
				session['login'] = 1
				session['user'] = auth['value']
			raise web.seeother('/')

app = web.application(urls,locals())
application = app.wsgifunc()

if	web.config.get('_session') is None:
	session = web.session.Session(
			app,
			web.session.DiskStore(os.path.join(settings.app_path,'sessions')),
			initializer = {'login':0,'user':''})
	web.config._session = session
else:
	session = web.config._session

if __name__=="__main__":
	app.run()
