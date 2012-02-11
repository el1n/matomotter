#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import cgi
import time
import Cookie
import twiauth
import libGAEsession

CALLBACK_URI = "http://localhost:8080/sample4.py"

def main():
	cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE",""))
	session = libGAEsession.session_memcache()
	param = cgi.FieldStorage()
	oauth_token = param.getvalue("oauth_token","error").decode("utf-8")
	oauth_verifier = param.getvalue("oauth_verifier","error").decode("utf-8")
	t = twiauth.geturl(CALLBACK_URI)

	if cookie.has_key("sessionid"):
		if session.load(cookie["sessionid"].value.decode("ascii")) == None:
			session.new()
		elif param.has_key("oauth_token") and param.has_key("oauth_verifier"):
                        ak = twiauth.getatoken(oauth_token, oauth_verifier, session.get("token_secret"))
                        print u"uhyo-"
                        print u"welcome @" + ak[0]
                        print u"your access key is " + ak[1]
                        print u""
                        print u""
        
	session.set("i",session.get("i",0) + 1)
        session.set("token_secret",t[2])

	print "Set-Cookie: sessionid=%s; expires=%s; path=/" % (session.getid(),time.strftime("%a, %d-%b-%Y %H:%M:%S GMT",time.gmtime(time.time() + 86400)))
	print "Content-Type: text/html"
	print ""
	print "id = %s" % (session.getid())
	print session.get("i")
        print t[1]
        print u"<br>"
        print 
	session.save()
	
	

if __name__ == "__main__":
	main()
