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

def main():

	HOME_URI = conf.dict['HOME_URI']

	cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE","")) # クッキーおいしいです
	session = libGAEsession.session_memcache() # セッションDB
	dbq = libmatomotter.q() # 質問用DB
	dba = libmatomotter.a() # 回答用DB
	param = cgi.FieldStorage()
	auth = tweepy.OAuthHandler(conf.dict['consumer_key'], conf.dict['consumer_secret'], HOME_URI+"?m=callback", True) # tweepy(TwitterAPI)にConsumer keyくわせる
	api = tweepy.API(auth)

	if cookie.has_key("sessionid"): # クッキー埋め込み
		if session.load(cookie["sessionid"].value.decode("ascii")) == None:
			session.new()

	# HTTP共通ヘッダ部
	print u"Set-Cookie: sessionid=%s; expires=%s; path=/" % (session.getid(),time.strftime("%a, %d-%b-%Y %H:%M:%S GMT",time.gmtime(time.time() + 86400)))
	print u"Content-Type: text/html; charset=UTF-8"

	try: # モード取得
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


	else: # デフォルト（トップページ）
		print u""
		print login_status(session.get("screen_name",""))+u"<br>"
		print u"トップペーーーーージ＾ｑ＾"
		spam = ("1","2","3","4","5","6")
		print spam
		for i in spam:
			spam = spam[1:]
			print spam
			print str(len(spam))+u"<BR>"