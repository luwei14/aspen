"""
Models for aspen.py
"""
import os
import re
import web
import settings
from utilities import mdrender,decrypt
from datetime import datetime,timedelta

app_path = os.path.dirname(__file__)

############################  init template render ############################
t_globals = dict(
	datestr = web.datestr,
)

# templates path, absolute path
templates = os.path.join(app_path, "templates")

# template render
render = web.template.render(templates, 
							 base="base",
							 cache = settings.CACHE,
							 globals = t_globals)

render._keywords['globals']['render'] = render

############################# database handle #################################
DB = web.database(dbn=settings.DBTYPE,db=settings.DATAPATH)

def preprocess(text):
	lines=re.split("\n",text)
	tbody = ""
	metadata = {}
	for line in lines:
		if re.match('^%',line):
			item = line[1:len(line)].strip().split(":")
			metadata[item[0].strip()] = item[1].strip()
		else:
			tbody += ( "\n"+line)
	return metadata,tbody

def preprocesspost(po):
	post={}
	post["title"] = po["title"]
	post["content"] = po["content"]
	metadata,tbody = preprocess(po["content"])
	if metadata.has_key("title_id"):
		post["title_id"] = metadata["title_id"]
	else:
		ut = datetime.utcnow() + timedelta(hours=8)
		ut = ut.strftime("%Y%m%d%H%M%S")
		post["title_id"] = "post_"+ut
	
	if metadata.has_key("tags"):
		tags = metadata["tags"].split(",")
		for i in range(len(tags)):
			tags[i] = tags[i].strip()
		metadata["tags"] = ",".join(tags)
		post["tags"] = metadata["tags"]
	else:
		post["tags"]=""

	if metadata.has_key("category"):
		post["category"] = metadata["category"]
	else:
		post["category"] = "Uncategorized"
	
	if metadata.has_key("type"):
		post["type"] = int(metadata["type"])
	else:
		post["type"] = 0
	print post
	return post

######################## functions for the aspen.py ###########################
def getUserInfo():
	'''
		get user's information
	'''
	user = DB.select(settings.TBL_USER)[0]
	#profile2html = mdrender.mdrender(user["profile"])
	#user["profile"] = profile2html
	return user

def getRecentPosts(private=False):
	'''
		get 5 of recently published posts
	'''
	what = "title, title_id, create_time, update_time, type"
	cond = "type = 1"
	order = "create_time DESC"
	posts = None
	if private is True:
		posts = DB.select(settings.TBL_POST,what=what, order=order,limit=5)
	else:
		posts = DB.select(settings.TBL_POST,what=what, where=cond, order=order,limit=5)
	return list(posts)

def getPostById(title_id,private=False,edit=False):
	'''
		get a post by title_id if it is type is 1, or published	
	'''
	cond = ""
	if private is True:
		cond = "title_id is '%s'" % title_id	
	else:
		cond = "title_id is '%s' and type = 1" % title_id
	posts = DB.select(settings.TBL_POST,where=cond)
	posts = list(posts)
	if len(posts) ==0:
		return None
	else:
		post = posts[0]
		if edit is False:
			metadata,tbody = preprocess(post['content'])
			con2html = mdrender.mdrender(tbody)		
			post['content'] = con2html
		return post

def getAllPosts(private=False):
	'''
		get all published posts	
	'''
	cond = "type = 1"
	what = "title, title_id, create_time, update_time, type"
	order = "create_time DESC"
	posts = None
	if private is True:
		posts = DB.select(settings.TBL_POST,what=what, order=order)
	else:
		posts = DB.select(settings.TBL_POST,what=what, where=cond, order=order)
	return list(posts)

def getAllTags():
	'''
		get all tags have been used	in published posts
	'''
	tags = DB.select(settings.TBL_TAG)
	tags = list(tags)
	retags = []
	for t in tags: retags.append(t)
	k = []
	for i in range(len(tags)):
		cond = "type = 1 and tags like '%%%s%%'" % tags[i]['name']
		re = DB.select(settings.TBL_POST,where=cond)
		re = list(re)
		if len(re) == 0:
			k.append(i)
		else:
			retags[i]['frequency'] = len(re)
	for i in k:
		retags.remove(tags[i])
	return retags

def getAllCategory():
	'''
		get all tags have been used, in published posts
	'''
	categories = DB.select(settings.TBL_CATEGORY)
	categories = list(categories)
	recate = []
 	for c in categories: recate.append(c)
	k = []
	for i in range(len(categories)):
		cond = "type = 1 and category is '%s'" % categories[i]['name']
		re = DB.select(settings.TBL_POST,where=cond)
		re = list(re)
		if len(re) == 0:
			k.append(i)
		else:
			recate[i]['frequency'] = len(re)
	for i in k:
		recate.remove(categories[i])
	return recate

def getPostByTag(tagid,private=False):
	'''
		get all the published posts by tag id	
	'''
	cond = "id is %d" % tagid
	tag = DB.select(settings.TBL_TAG,where = cond)
	tag = list(tag)
	if len(tag) == 0:
		return None
	tag = tag[0]
	cond1 = ""
	if private is True:
		cond1 = "tags like '%%%s%%'" % tag['name']
	else:
		cond1 = "tags like '%%%s%%' and type = 1" % tag['name']
	what = "title, title_id, create_time, update_time, type"
	order = "create_time DESC"
	posts = DB.select(settings.TBL_POST,where=cond1,what=what,order=order)
	return {'posts':list(posts),'tag':tag['name']}

def getPostByCategory(cateid,private=False):
	'''
		get all the published posts by category id	
	'''
	cond = "id is %d" % cateid
	cate = DB.select(settings.TBL_CATEGORY,where = cond)
	cate = list(cate)
	if len(cate) == 0:
		return None
	cate = cate[0]
	cond1 = ""
	if private is True:
		cond1 = "category is '%s'" % cate['name']
	else:
		cond1 = "category is '%s' and type = 1" % cate['name']
	what = "title, title_id, create_time, update_time, type"
	order = "create_time DESC"
	posts = DB.select(settings.TBL_POST,where=cond1,what=what,order=order)
	return {'posts':list(posts),'category':cate['name']}

######################## functions for the admin.py ###########################
def userAuth(name,pwd):
	'''
		authenticate user	
	'''

	# fetch the user by name
	cond = "username is '" + name + "'"
	user = DB.select(settings.TBL_USER, where = cond)
	user = list(user)

	# user name error
	if len(user) == 0:
		auth = {"error": 1, "msg": "No Such User %s" % name, "value": None}
		return auth

	# if find a user, check the password
	user = user[0]
	check = decrypt.checkpwd(pwd,user['pwd'])

	# password is not right
	if check is False:
		auth = {"error": 2, "msg": "Passward does not match.", "value": None} 
		return auth
	
	# if password matches, return the user by value, no error, no msg
	auth = {"error": 0, "msg": None, "value": user}
	return auth

def updateUserInfo(info):
	'''
		update user information	
	'''
	user = getUserInfo()
	cond = "id = %d" % user['id']
	try:
		DB.update(settings.TBL_USER, where = cond, username = info['username'],
			realname = info['realname'],
			title = info['title'], dept = info['dept'], dept_l = info['dept_l'],
			comp = info['comp'], comp_l = info['comp_l'], addr1= info['addr1'],
			addr2 = info['addr2'], zip = info['zip'], email = info['email'],
			tel = info['tel'], wgs_lon = info['wgs_lon'], wgs_lat = info['wgs_lat'],
			profile = info['profile']
		)
		return getUserInfo()
	except:
		return None

def getTag(**k):
	tags = DB.select(settings.TBL_TAG,**k)
	tagslist = list(tags)
	return tagslist

def getCategory(**k):
	category = DB.select(settings.TBL_CATEGORY,**k)
	categorylist = list(category)
	return categorylist

def upsertTags(tags):
	'''
		insert or update tags
		eg: tags = ['Python', 'Big Data']
	'''
	for tag in tags:
		res = DB.select(settings.TBL_TAG,where="lower(name) is '%s'" % tag.lower())
		res = list(res)
		if len(res) == 0:
			# does not exist, insert one
			DB.insert(settings.TBL_TAG,name=tag)
		else:
			# exists, increase frequency
			DB.update(settings.TBL_TAG,"lower(name) is '%s'" % tag.lower(), frequency=res[0]['frequency']+1)

def tagde(tags):
	'''
		when tag changed, maintain the frequency field	
	'''
	for tag in tags:
		res = DB.select(settings.TBL_TAG,where="lower(name) is '%s'" % tag.lower())
		res = list(res)
		DB.update(settings.TBL_TAG,"lower(name) is '%s'" % tag.lower(), frequency=res[0]['frequency']-1)

def upsertCategory(category):
	'''
		insert or update categories
		eg: categories = ['Python', 'Big Data']
	'''
	res = DB.select(settings.TBL_CATEGORY,where="lower(name) is '%s'" % category.lower())
	res = list(res)
	if len(res) == 0:
		# does not exist, insert one
		DB.insert(settings.TBL_CATEGORY,name=category)
	else:
		# exists, increase frequency
		DB.update(settings.TBL_CATEGORY,"lower(name) is '%s'" % category.lower(), frequency=res[0]['frequency']+1)

def categoryde(category):
	'''
		when category changed, maintain the frequency field	
	'''
	res = DB.select(settings.TBL_CATEGORY,where="lower(name) is '%s'" % category.lower())
	res = list(res)
	DB.update(settings.TBL_CATEGORY,"lower(name) is '%s'" % category.lower(), frequency=res[0]['frequency']-1)

def newPost(post):
	'''
		add a new post
		eg:post = {'title':'webpy development',...}	
	'''
	tags = post['tags'].split(',')
	category = post['category']
	try:
		ut = datetime.utcnow() + timedelta(hours=8)
		ut = ut.strftime("%Y-%m-%d %H:%M:%S")
		DB.insert(settings.TBL_POST, title=post['title'],
		title_id=post['title_id'], tags=post['tags'],category=post['category'],
		content = post['content'], create_time = ut,update_time = ut,type=post['type'])
	except:
		return False
	# if inserting successed, update the tag and category table
	upsertTags(tags)
	upsertCategory(category)
	return True

def updatePost(post,prepost):
	tags = post['tags'].split(',')
	category = post['category']

	try:
		ut = datetime.utcnow() + timedelta(hours=8)
		ut = ut.strftime("%Y-%m-%d %H:%M:%S")
		cond = "title_id is '%s'" % prepost['title_id']
		DB.update(settings.TBL_POST, where=cond, title=post['title'],
		tags=post['tags'],category=post['category'],
		content = post['content'], update_time = ut,type=post['type'])
	except:
		return False
	#old tags
	tags1 = prepost['tags'].split(',')
	
	# deleted tags
	tde = list(set(tags1)-set(tags))
	# new added tags
	tadd = set(tags)-set(tags1)
	# decrease the frequency of the deleted tags
	tagde(tde)
	# insert or update the new tags
	upsertTags(tadd)
	# if category changed, decrease the frequency of the pre category,
	# and insert the new category, or update the frequency of new category
	if prepost['category'] != post['category']:
		categoryde(prepost['category'])
		upsertCategory(category)	
	return True

def deletePost(title_id):
	cond = "title_id = '%s'" % title_id
	post = DB.select(settings.TBL_POST,where=cond)[0]
	DB.delete(settings.TBL_POST,where=cond)
	tagde(post['tags'].split(','))
	categoryde(post['category'])

def setnewpwd(pwd):
	user = getUserInfo()
	enpwd = decrypt.encrypt(pwd)
	DB.update(settings.TBL_USER,where="username is '%s'" % user['username'], pwd=enpwd)
