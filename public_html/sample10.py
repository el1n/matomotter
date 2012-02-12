#!/usr/bin/python
# -*- coding: utf-8 -*-
# coding: UTF-8

import os
import sys
import codecs
import cgi
import time
import Cookie
import tweepy
import libGAEsession
import conf


HOME_URI = "http://localhost:8080/test/"

def main():

	sys.stdout = codecs.getwriter("utf-8")(sys.stdout) # クソ文字コード処理対策
	cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE","")) # クッキーおいしいです
	session = libGAEsession.session_memcache() # セッションDB
	param = cgi.FieldStorage()
	auth = tweepy.OAuthHandler(conf.dict['consumer_key'], conf.dict['consumer_secret'], HOME_URI+"?m=callback", True) # tweepyにConsumer keyくわせる
	api = tweepy.API(auth)

	if cookie.has_key("sessionid"): # クッキー埋め込み
		if session.load(cookie["sessionid"].value.decode("ascii")) == None:
			session.new()

	m = param.getvalue("m","").decode("utf-8") # モード取得

	# HTTP共通ヘッダ部
	print u"Set-Cookie: sessionid=%s; expires=%s; path=/" % (session.getid(),time.strftime("%a, %d-%b-%Y %H:%M:%S GMT",time.gmtime(time.time() + 86400)))
	print u"Content-Type: text/html; charset=UTF-8"


	if m == "login": # 認証前処理

		if session.get("access_key",None) == None:
			url = auth.get_authorization_url()
			session.set("token_secret", auth.request_token.secret)
			session.save()
			print u"Location:"+url
		else:
			auth.set_access_token(session.get("access_key"),session.get("access_secret"))

			try:
				auth.get_username()
				url = HOME_URI
				session.set("id",api.me().id)
				session.set("screen_name",api.me().screen_name)
			except:
				url = auth.get_authorization_url()
				session.set("token_secret", auth.request_token.secret)
			finally:
				print u"Location:"+url

			session.save()


	elif m == "callback": # 認証後処理

		oauth_token = param.getvalue("oauth_token","").decode("utf-8")
		oauth_verifier = param.getvalue("oauth_verifier","").decode("utf-8")

		try:
			auth.set_request_token(oauth_token,session.get("token_secret"))
			auth.get_access_token(oauth_verifier)
			session.set("access_key",auth.access_token.key)
			session.set("access_secret",auth.access_token.secret)
			auth.set_access_token(session.get("access_key"),session.get("access_secret"))
			session.set("id",api.me().id)
			session.set("screen_name",api.me().screen_name)
			url = HOME_URI
		except:
			url = HOME_URI+"?m=login"
		finally:
			print u"Location:"+url

		session.save()


	elif m == "logout": # ログアウト処理

		session.set("id",None)
		session.set("screen_name",None)
		session.set("access_key",None)
		session.set("access_secret",None)
		session.save()
		print u"Location:"+HOME_URI


	else: # トップペーーーージ

		print u""

		try:
			auth.set_access_token(session.get("access_key"),session.get("access_secret"))
			username = auth.get_username()
			user_status = u'Logged in as @' + username + "(" + str(session.get("id")).encode("utf-8") + ") "
		except:
			user_status = u'<a href="?m=login">Login</a>'
		finally:
			print user_status
			print u'<a href="?m=logout">Logout</a>'


if __name__ == "__main__":
	main()
