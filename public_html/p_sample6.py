#!/usr/bin/python
# -*- coding: utf-8 -*-
# coding: UTF-8

import os
import cgi
import time
import Cookie
import tweepy
import libGAEsession
import conf

CALLBACK_URI = "http://localhost:8080/sample6.py"

def main():
	cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE",""))
	session = libGAEsession.session_memcache()
	param = cgi.FieldStorage()
	oauth_token = param.getvalue("oauth_token","").decode("utf-8")
	oauth_verifier = param.getvalue("oauth_verifier","").decode("utf-8")

	auth = tweepy.OAuthHandler(conf.dict['consumer_key'], conf.dict['consumer_secret'], CALLBACK_URI, True)
	api = tweepy.API(auth)

	if cookie.has_key("sessionid"):
		if session.load(cookie["sessionid"].value.decode("ascii")) == None:
			session.new()

	if param.has_key("oauth_token") and param.has_key("oauth_verifier") and not session.get("token_secret",None) == None:
		auth.set_request_token(oauth_token,session.get("token_secret"))
		auth.get_access_token(oauth_verifier)
		session.set("access_key",auth.access_token.key)
		session.set("access_secret",auth.access_token.secret)
		auth.set_access_token(session.get("access_key"),session.get("access_secret"))

		session.set("id",api.me().id)
		session.set("screen_name",api.me().screen_name)

	print "Set-Cookie: sessionid=%s; expires=%s; path=/" % (session.getid(),time.strftime("%a, %d-%b-%Y %H:%M:%S GMT",time.gmtime(time.time() + 86400)))
	print "Content-Type: text/html"
	print ""

	if session.get("id",None) == None:
		auth_url = auth.get_authorization_url()
		session.set("token_secret", auth.request_token.secret)
		print u'<a href="' + auth_url + u'">Login</a>'

	else:
		print u"logged in as @" + session.get("screen_name").encode("utf-8") + "<br>"
		auth.set_access_token(session.get("access_key"),session.get("access_secret"))
		postvalue = u"APIからテスト投稿（tweepy使用）"
		try:
			api.update_status(postvalue)
		except:
			print u"Post Error"

	session.save()


if __name__ == "__main__":
	main()
