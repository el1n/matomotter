#!/usr/bin/python
import os
import time
import Cookie
import libsess

def main():
	cookie = Cookie.SimpleCookie()
	session = libsess.sei()

	if os.environ.has_key("HTTP_COOKIE"):
		cookie.load(os.environ["HTTP_COOKIE"])
		if cookie.has_key("sessionid"):
			if session.load(cookie["sessionid"].value) == None:
				session.new()

	session.set("i",session.get("i",0) + 1)

	print "Set-Cookie: sessionid=%s; expires=%s; path=/" % (session.id_(),time.strftime("%a, %d-%b-%Y %H:%M:%S GMT",time.gmtime(time.time() + 86400)))
	print "Content-Type: text/html"
	print ""
	print "id = %s" % (session.id_())
	print session.get("i")

	session.save()

if __name__ == "__main__":
	main()
