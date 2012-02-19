#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import random
import cgi
import time
import Cookie
import tweepy
import libmatomotter
import libGAEsession
import conf

def login_status(screen_name):
	if screen_name:
		r = u"Logged in as @"+screen_name+u' <a href="?m=logout">Logout</a>'
	else:
		r = u'<a href="?m=login">Login</a>'
	return r

def get_userlist(access_key,access_secret,uid):
	auth = tweepy.OAuthHandler(conf.dict['consumer_key'], conf.dict['consumer_secret']) # tweepy(TwitterAPI)にConsumer keyくわせる
	auth.set_access_token(access_key,access_secret)
	api = tweepy.API(auth)
	id_list = api.friends_ids()
	users = []
	if uid:
		users.append(uid)
		try:
			id_list.remove(uid)
		except:
			pass
	return_friends = []
	while len(users) < 5 and len(id_list) > 0: # 5件格納 or idのストックがなくなるまでルーーーープ
		users.append(id_list.pop(random.randint(0,len(id_list)-1))) # どんどん格納する
	for i in api.lookup_users(users):
		return_friends.append(i) # どんどん格納する
	return return_friends

def main():

	HOME_URI = conf.dict['HOME_URI']

	cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE","")) # クッキーおいしいです
	session = libGAEsession.session_memcache() # セッションDB
	dbq = libmatomotter.q() # 質問用DB
	dba = libmatomotter.a() # 回答用DB
	param = cgi.FieldStorage()
	auth = tweepy.OAuthHandler(conf.dict['consumer_key'], conf.dict['consumer_secret'], HOME_URI, True) # tweepy(TwitterAPI)にConsumer keyくわせる
	api = tweepy.API(auth)

	if cookie.has_key("sessionid"): # クッキー埋め込み
		if session.load(cookie["sessionid"].value.decode("ascii")) == None:
			session.new()

	# HTTP共通ヘッダ部
	print u"Set-Cookie: sessionid=%s; expires=%s; path=/" % (session.getid(),time.strftime("%a, %d-%b-%Y %H:%M:%S GMT",time.gmtime(time.time() + 86400)))
	print u"Content-Type: text/html; charset=UTF-8"

	try: # 外部モード取得
		m = param.getvalue("m","").decode("utf-8")
	except: # こけたらクリアする
		m = None
	in_mode = session.get("in_mode",()) # 内部モード取得


	# 内部モード処理開始
	if len(in_mode):
		if in_mode[0] == "callback": # ログイン後処理
			try:
				auth.set_request_token(param.getvalue("oauth_token","").decode("utf-8"),session.get("token_secret"))
				auth.get_access_token(param.getvalue("oauth_verifier","").decode("utf-8"))
				session.set("access_key",auth.access_token.key)
				session.set("access_secret",auth.access_token.secret)
				auth.set_access_token(session.get("access_key"),session.get("access_secret"))
				session.set("id",api.me().id)
				session.set("screen_name",api.me().screen_name)
				url = HOME_URI
				session.set("in_mode",in_mode[1:])
			except:
				url = auth.get_authorization_url()
				session.set("token_secret", auth.request_token.secret)
			finally:
				m = "blank"
				print u"Location:"+url
			session.save()

		elif in_mode[0] == "post_q": # 質問投稿
			if session.get("id",None):
				q = session.get("temp_q")
				q["id"] = session.get("id")
				q["screen_name"] = session.get("screen_name")
				url = HOME_URI+u"?m=q&id="+str(dbq.set(q))
				session.set("in_mode",in_mode[1:])
				print u"Location:"+url
				m = "blank"
				session.save()

		elif in_mode[0] == "return_page": # もどれ
			if session.get("id",None):
				session.set("in_mode",in_mode[1:])
				print u"Location:"+HOME_URI+u"?"+session.get("return_to")
				m = "blank"
				session.save()

	# 外部モード処理開始
	if m == "blank": # 空白
		print u""

	elif m == "login": # ログイン処理
		url = auth.get_authorization_url()
		session.set("token_secret", auth.request_token.secret)
		session.set("in_mode",("callback",)+session.get("in_mode",()))
		print u"Location:"+url
		session.save()

	elif m == "logout": # ログアウト処理
		session.clear()
		session.save()
		print u"Location:"+HOME_URI

	elif m == "make": # 質問作成ペーーーージ
		if param.getvalue("post_flg","").decode("utf-8"):
			if session.get("id",None):
				q = {
					"theme":param.getvalue("theme","").decode("utf-8"),
					"option0":param.getvalue("option0","").decode("utf-8"),
					"option1":param.getvalue("option1","").decode("utf-8"),
					"option2":param.getvalue("option2","").decode("utf-8"),
					"option3":param.getvalue("option3","").decode("utf-8"),
					"id":session.get("id"),
					"screen_name":session.get("screen_name")
				}
				url = HOME_URI+u"?m=q&id="+str(dbq.set(q))

			else:
				q = {
					"theme":param.getvalue("theme","").decode("utf-8"),
					"option0":param.getvalue("option0","").decode("utf-8"),
					"option1":param.getvalue("option1","").decode("utf-8"),
					"option2":param.getvalue("option2","").decode("utf-8"),
					"option3":param.getvalue("option3","").decode("utf-8")
				}
				session.set("temp_q",q)
				session.set("in_mode",("post_q",))
				url = HOME_URI+u"?m=login"

			print u"Location:"+url
			session.save()

		else:
			print login_status(session.get("screen_name",""))+u"<br>"
			print u'<form method="post" action="?m=make">'
			print u'<input type="hidden" name="post_flg" value="1">'
			print u'<input type="text" name="theme" value=""><br>'
			print u'<input type="text" name="option0" value="">'
			print u'<input type="text" name="option1" value="">'
			print u'<input type="text" name="option2" value="">'
			print u'<input type="text" name="option3" value=""><br>'
			print u'<input type="submit" value="Post">'
			print u'</form>'

	elif m == "q": # 回答ペーーーーーージ
		if not session.get("id",None) and not param.getvalue("uid",None):
			session.set("return_to",os.environ['QUERY_STRING'])
			session.set("in_mode",("return_page",))
			print u"Location:"+HOME_URI+u"?m=login"
		elif session.get("id",None):
			r = dbq.get(int(param.getvalue("id")))
			o = (r.get("option0",None),r.get("option1",None),r.get("option2",None),r.get("option3",None))
			print u""
			print login_status(session.get("screen_name",""))+u"<br>"
			print u'質問に答えるのれす^q^<br>'
			print u"しつもん: "+r.get("theme",None)+u"<br>"
			print u'<form method="post" action="?m=a&id='+param.getvalue("id")+u'">'
			for i in get_userlist(session.get("access_key"),session.get("access_secret"),param.getvalue("uid",None)):
				print i.screen_name+u'さん'
				c = 0
				for i2 in o:
					print u'<input type="radio" name="'+i.screen_name+'" value="'+str(c).encode("utf-8")+'">'+i2
					c = c + 1
				print u'<br>'
			print u'<input value="Answer!" type="submit">'
			print u'</form>'


		else:

			print u""
			print login_status(session.get("screen_name",""))+u"<br>"
			print u'質問に答えるのれす^q^<br>'
			r = dbq.get(int(param.getvalue("id")))
			print u"しつもん: "+r.get("theme",None)+u"<br>"
			print u'<form method="post" action="?m=a&id='+param.getvalue("id")+u'">'
			print u'<input name="0" value="'+r.get("option0",None)+u'" type="submit">'
			print u'<input name="1" value="'+r.get("option1",None)+u'" type="submit">'
			print u'<input name="2" value="'+r.get("option2",None)+u'" type="submit">'
			print u'<input name="3" value="'+r.get("option3",None)+u'" type="submit">'
			print u'</form>'

	elif m == "a": # 回答処理
		print param
		print os.environ['QUERY_STRING']
#		if session.get("id",None):
#			a = {
#				
#				"qid":param.getvalue("id").decode("utf-8"),
#				"referred_id":param.getvalue("uid").decode("utf-8"),
#				"referred_screen_name":(api.get_user(param.getvalue("uid").decode("utf-8"))).screen_name,
#				"choice":o,
#				"referring_id":session.get("id"),
#				"referring_screen_name":session.get("screen_name")
#				}
#			url = HOME_URI+u"?m=q&id="+str(dbq.set())


	else: # デフォルト（トップページ）
		print u""
		print login_status(session.get("screen_name",""))+u"<br>"
		print u"トップペーーーーージ＾ｑ＾"
		print u'<a href="?m=make">Make Question</a><br>'