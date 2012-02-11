#!/usr/bin/python
import cgi
import libmatomotter

def main():
	db = libmatomotter.q()

	param = cgi.FieldStorage()
	if param.getvalue("q"):
		r = db.get(int(param.getvalue("q")))
		if r != None:
			print u"Content-Type: text/html"
			print
			print u"id = "+str(r.get("id",None))
			print u"screen_name = "+r.get("screen_name",None)
			print u"subject = "+r.get("subject",None)
			print u"option0 = "+r.get("option0",None)
		else:
			print u"Content-Type: text/html"
			print
			print u"id notfound"
	else:
		q = {
			"id":123,
			"screen_name":"foo",
			"subject":"subject",
			"option0":"option0"
		}

		print u"Content-Type: text/html"
		print
		print db.set(q)
		print u"saved."

if __name__ == "__main__":
	main()
