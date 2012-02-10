#!/usr/bin/python
import os
import time
import Cookie
import libGAEsession

def main():
	cookie = Cookie.SimpleCookie(os.environ.get("HTTP_COOKIE",""))
	#session = libGAEsession.session()
	session = libGAEsession.session_memcache()

	if cookie.has_key("sessionid"):
		if session.load(cookie["sessionid"].value.decode("ascii")) == None:
			session.new()

	session.set("i",session.get("i",0) + 1)

	print "Set-Cookie: sessionid=%s; expires=%s; path=/" % (session.getid(),time.strftime("%a, %d-%b-%Y %H:%M:%S GMT",time.gmtime(time.time() + 86400)))
	print "Content-Type: text/html"
	print ""
	print "id = %s" % (session.getid())
	print session.get("i")

	session.save()

if __name__ == "__main__":
	main()
