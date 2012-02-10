#!/usr/bin/python
import os
import time
import Cookie
import twiauth
import libGAEsession

CALLBACK_URI = "http://localhost:8080/sample4.py"

def main():

        cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE",""))
	session = libGAEsession.session()

	if cookie.has_key("sessionid"):
		if session.load(cookie["sessionid"].value) == None:
			session.new()
        
	session.set("i",session.get("i",0) + 1)

	t = twiauth.geturl(CALLBACK_URI)

	print "Set-Cookie: sessionid=%s; expires=%s; path=/" % (session.getid(),time.strftime("%a, %d-%b-%Y %H:%M:%S GMT",time.gmtime(time.time() + 86400)))
	print "Content-Type: text/html"
	print ""
	#print "id = %s" % (session.getid())
	#print session.get("i")
        print t[0]
        print t[1]
        print t[2]
	session.save()
	
	

if __name__ == "__main__":
	main()
