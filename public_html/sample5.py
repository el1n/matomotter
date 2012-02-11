#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import cgi
import time
import Cookie
import twiauth
import libGAEsession

CALLBACK_URI = "http://localhost:8080/sample5.py"

def main():
	cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE",""))
	session = libGAEsession.session_memcache()
	param = cgi.FieldStorage()
	oauth_token = param.getvalue("oauth_token","error").decode("utf-8")
	oauth_verifier = param.getvalue("oauth_verifier","error").decode("utf-8")

        logon = False

	if cookie.has_key("sessionid"):
            if session.load(cookie["sessionid"].value.decode("ascii")) == None:
                session.new()

	if param.has_key("oauth_token") and param.has_key("oauth_verifier"):
            ak = twiauth.getatoken(oauth_token, oauth_verifier, session.get("token_secret"))
            session.set("access_key", ak[1])
            logon = True

        print "Set-Cookie: sessionid=%s; expires=%s; path=/" % (session.getid(),time.strftime("%a, %d-%b-%Y %H:%M:%S GMT",time.gmtime(time.time() + 86400)))
	print "Content-Type: text/html"
	print ""
            
        if logon == False:
            t = twiauth.geturl(CALLBACK_URI)
            session.set("token_secret", t[2])
            print u'<a href="' + t[1] + u'">Login</a>'
        else:
            print u"logged in as @" + ak[0] + "<br>"

	session.save()
	
	

if __name__ == "__main__":
	main()